import torch
import torch.nn as nn
import torch.nn.functional as F

from .ff import FeedForward, GatedFeedForward

class MoeRouter(nn.Module):
    """Mixture-of-Experts Router layer - computes routing weights for each expert."""

    def __init__(self, embed_dim: int, num_experts: int, top_k: int = 1, *args, **kwargs):
        super(MoeRouter, self).__init__(*args, **kwargs)
        self.top_k = top_k
        self.num_experts = num_experts
        self.gate = nn.Linear(embed_dim, num_experts, bias=False)
        # For expert load balancing
        self.register_buffer('aux_loss', torch.tensor(0.0), persistent=False)

    # def calculate_aux_loss(self, top_k_indices: torch.Tensor, probs: torch.Tensor) -> torch.Tensor:
    #     expert_mask = F.one_hot(top_k_indices, self.num_experts).float()
    #     expert_usage = expert_mask.sum(dim=0).mean(dim=0)
    #     mean_probs = probs.mean(dim=0)
    #     return (expert_usage * mean_probs).sum() * self.num_experts

    def calculate_aux_loss(self, top_k_indices: torch.Tensor, probs: torch.Tensor) -> torch.Tensor:
        # Get shapes
        T, K = top_k_indices.size()  # Batch, Sequence length, Top-K

        # 1. Compute expert selection mask (one-hot encoded)
        expert_mask = F.one_hot(top_k_indices, self.num_experts).to(dtype=probs.dtype)  # (B, S, K, E)

        # 2. Total number of times each expert is selected
        expert_usage = expert_mask.sum(dim=(0, 1))  # (E,)

        # 3. Fraction of tokens assigned to each expert
        total_selections = T * K
        fraction_expert = expert_usage / (total_selections + 1e-6)  # (E,)

        # 4. Sum of probabilities for each expert's selected tokens
        probs_expanded = probs.unsqueeze(1).expand(-1, K, -1)  # (B_K, K, E)
        sum_probs = (probs_expanded * expert_mask).sum(dim=(0, 1))

        # 5. Average probability per expert (avoid division by zero)
        avg_probs = sum_probs / expert_usage.clamp(min=1e-6)  # (E,)

        # 6. Compute load balancing loss
        loss = (fraction_expert * avg_probs).sum() * self.num_experts

        return loss

    def forward(self, x: torch.Tensor):
        # Input shape: [batch*seq_len, embed_dim]
        logits = self.gate(x)
        probs = F.softmax(logits, dim=-1)
        # Get top-k experts for each token
        top_k_weights, top_k_indices = probs.topk(self.top_k, dim=-1)

        # Normalize weights (sum to 1 for each token)
        top_k_weights = top_k_weights / (top_k_weights.sum(dim=-1, keepdim=True) + 1e-9)
        # Load Balance Loss
        if self.training:
            self.aux_loss = self.calculate_aux_loss(top_k_indices, probs)

        return top_k_weights, top_k_indices


class MoeFeedForward(nn.Module):
    """Mixture-of-Experts Feed-Forward layer - combines multiple experts into a single model."""

    def __init__(
            self,
            embed_dim: int,
            hidden_dim: int,
            num_experts: int,
            activation: nn.Module,
            top_k: int = 1,
            dropout: float = 0.0,
            *args,
            **kwargs
    ):
        super(MoeFeedForward, self).__init__(*args, **kwargs)
        self.embed_dim = embed_dim
        self.num_experts = num_experts
        self.top_k = top_k
        self.capacity_factor = 1.5

        self.router = MoeRouter(embed_dim, num_experts, top_k)

        # Batch all expert parameters together
        self._init_experts(num_experts, embed_dim, hidden_dim, activation, dropout)

    def _init_experts(self, num_experts: int, embed_dim: int, hidden_dim: int, activation: nn.Module, dropout: float):
        self.experts = nn.ModuleList([
            FeedForward(embed_dim, hidden_dim, activation, dropout)
            for _ in range(num_experts)
        ])

    def router_loss(self):
        return self.router.aux_loss

    def forward(self, x: torch.Tensor):
        orig_shape = x.size()
        x = x.view(-1, self.embed_dim)  # [batch*seq_len, embed_dim]

        # Get routing weights and indices
        weights, indices = self.router(x)  # [B*T, top_k], [B*T, top_k]

        # Create mask for expert contributions (B*T, num_experts)
        expert_mask = F.one_hot(indices, self.num_experts).to(dtype=weights.dtype)  # [B*T, top_k, num_experts]
        expert_weights = (weights.unsqueeze(-1) * expert_mask).sum(dim=1)  # [B*T, num_experts]

        output = torch.zeros_like(x)
        for expert_idx in range(self.num_experts):
            # Mask for tokens where this expert is in top_k
            mask = expert_weights[:, expert_idx] > 0
            if not mask.any():
                continue

            # Compute expert output for selected tokens
            expert_input = x[mask]
            expert_output = self.experts[expert_idx](expert_input)

            # Apply combined weights for this expert
            output[mask] += expert_output * expert_weights[mask, expert_idx].unsqueeze(-1)

        return output.view(*orig_shape)

    # def forward(self, x: torch.Tensor) -> torch.Tensor:
    #     # Zapamiętanie oryginalnego kształtu wejścia w celu odtworzenia go na wyjściu.
    #     orig_shape = x.size()
    #     # Spłaszczenie wejścia do 2D: [batch_size * seq_len, embed_dim]
    #     x = x.view(-1, self.embed_dim)
    #     num_tokens, embed_dim = x.size()
    #
    #     # === KROK 1: ROUTING ===
    #     # Uzyskanie wag i indeksów k najlepszych ekspertów dla każdego tokenu.
    #     # routing_weights: [num_tokens, top_k]
    #     # selected_experts: [num_tokens, top_k]
    #     routing_weights, selected_experts = self.router(x)
    #
    #     # === KROK 2: TWORZENIE MAPY DYSPozytorskiej ===
    #     # Spłaszczenie indeksów ekspertów i wag do jednowymiarowych tensorów.
    #     # Każdy token jest teraz powielony 'top_k' razy, tworząc listę wszystkich przypisań.
    #     flat_selected_experts = selected_experts.view(-1)
    #     flat_routing_weights = routing_weights.view(-1)
    #
    #     # Stworzenie tensora z oryginalnymi indeksami tokenów.
    #     # Np. dla 3 tokenów i top_k=2, będzie to:
    #     token_indices = torch.arange(num_tokens, device=x.device).repeat_interleave(self.top_k)
    #
    #     # === KROK 3: PERMUTACJA (PRZETASOWANIE) ===
    #     # Stworzenie mapy permutacji przez posortowanie spłaszczonych indeksów ekspertów.
    #     # 'sorted_expert_indices' zawiera posortowane indeksy ekspertów.
    #     # 'sorted_order' to indeksy, które sortują oryginalne dane.
    #     sorted_expert_indices, sorted_order = flat_selected_experts.sort(0)
    #
    #     # Zastosowanie permutacji do przeorganizowania tokenów, ich oryginalnych indeksów i wag.
    #     # Teraz wszystkie tokeny dla eksperta 0 są na początku, potem dla eksperta 1, itd.
    #     permuted_token_indices = token_indices[sorted_order]
    #     permuted_routing_weights = flat_routing_weights[sorted_order]
    #     # Najważniejszy krok: fizyczne przeorganizowanie tensora wejściowego 'x'.
    #     dispatched_x = x[permuted_token_indices]
    #
    #     # === KROK 4: WSADOWE PRZETWARZANIE PRZEZ EKSPERTÓW ===
    #     # Obliczenie, ile tokenów trafiło do każdego eksperta.
    #     # 'tokens_per_expert' to tensor o długości 'num_experts', np. [10, 5, 0, 12,...]
    #     tokens_per_expert = F.one_hot(sorted_expert_indices, num_classes=self.num_experts).sum(dim=0)
    #
    #     # Obliczenie skumulowanej sumy, aby znać granice (początek i koniec) danych dla każdego eksperta.
    #     expert_boundaries = torch.cumsum(tokens_per_expert, dim=0)
    #
    #     # Przygotowanie listy na wyniki od ekspertów.
    #     expert_outputs = []
    #     start_idx = 0
    #     # Pętla po ekspertach - teraz jest wydajna, bo operuje na dużych, ciągłych wycinkach danych.
    #     for i in range(self.num_experts):
    #         num_tokens_for_expert = tokens_per_expert[i].item()
    #         if num_tokens_for_expert == 0:
    #             continue # Pomijamy ekspertów, którzy nie otrzymali żadnych tokenów.
    #
    #         end_idx = start_idx + num_tokens_for_expert
    #         # Wycięcie odpowiedniego fragmentu z przeorganizowanego tensora.
    #         expert_input = dispatched_x[start_idx:end_idx]
    #         # Przetworzenie danych przez eksperta.
    #         expert_output = self.experts[i](expert_input)
    #         expert_outputs.append(expert_output)
    #         start_idx = end_idx
    #
    #     # Połączenie wyników od wszystkich aktywnych ekspertów w jeden duży tensor.
    #     concatenated_outputs = torch.cat(expert_outputs, dim=0)
    #
    #     # === KROK 5: ODWRÓCENIE PERMUTACJI I POŁĄCZENIE WYNIKÓW ===
    #     # Zastosowanie wag routingu do wyników ekspertów.
    #     weighted_outputs = concatenated_outputs * permuted_routing_weights.unsqueeze(1)
    #
    #     # Stworzenie pustego tensora wyjściowego o tym samym kształcie i typie co spłaszczone wejście.
    #     final_output = torch.zeros_like(x)
    #
    #     # Stworzenie mapy odwrotnej permutacji, aby umieścić wyniki z powrotem na ich oryginalnych miejscach.
    #     # 'inverse_sorted_order' to indeksy, które przywracają oryginalną kolejność.
    #     inverse_sorted_order = sorted_order.argsort(0)
    #
    #     # Zastosowanie odwrotnej permutacji do wagowanych wyników.
    #     # Teraz wyniki są w tej samej kolejności co oryginalne przypisania token-ekspert.
    #     unpermuted_outputs = weighted_outputs[inverse_sorted_order]
    #
    #     # Stworzenie indeksów docelowych dla operacji scatter_add_.
    #     # Będą to oryginalne indeksy tokenów, powtórzone 'top_k' razy.
    #     scatter_indices = token_indices.unsqueeze(1).expand(-1, embed_dim)
    #
    #     # Użycie 'scatter_add_' do umieszczenia wyników w finalnym tensorze.
    #     # Ta operacja atomowo sumuje wkłady dla tokenów, które były przetwarzane przez wielu ekspertów.
    #     final_output.scatter_add_(0, scatter_indices, unpermuted_outputs)
    #
    #     # Przywrócenie oryginalnego kształtu tensora wyjściowego.
    #     return final_output.view(orig_shape)

    # def forward(self, x: torch.Tensor) -> torch.Tensor:
    #     # 0. Init steps
    #     # 0.1. Store original shape for final reshaping
    #     orig_shape = x.size()
    #     # 0.2. Flattening the input
    #     x = x.view(-1, self.embed_dim)
    #
    #     # 2. Routing - implemented internally in router
    #     routing_weights, selected_experts = self.router(x)
    #
    #     # 2. Prepare for disposition (Dispatch)
    #     # 2.1. Calculate capacity
    #     num_tokens = x.size(0)
    #     capacity = max(1, int((num_tokens * self.top_k / self.num_experts) * self.capacity_factor))
    #     # 2.2 Create expert one hot mask
    #     expert_mask = F.one_hot(selected_experts, num_classes=self.num_experts).to(x.dtype)
    #
    #     # 2.3. Calculate token in expert positions
    #     position_in_expert = torch.cumsum(expert_mask.view(-1, self.num_experts), dim=0) - 1
    #     position_in_expert = position_in_expert * expert_mask.view(-1, self.num_experts)
    #
    #     # 2.4. Discard overflowed tokens
    #     mask_within_capacity = position_in_expert < capacity
    #     expert_mask = expert_mask * mask_within_capacity.view(num_tokens, self.top_k, self.num_experts)
    #
    #     # 2.5. Recalculate positions in expert after discarding tokens
    #     position_in_expert = torch.cumsum(expert_mask.view(-1, self.num_experts), dim=0) - 1
    #     position_in_expert = position_in_expert * expert_mask.view(-1, self.num_experts)
    #     position_in_expert = position_in_expert.sum(dim=1)
    #
    #     # 2.6. Calculate flatten indices for scatter
    #     flat_selected_experts = selected_experts.view(-1)
    #     scatter_indices = (flat_selected_experts * capacity + position_in_expert).long()
    #
    #     # 3. Tokens disposition (Dispatch/Scatter)
    #     # 3.1. Create empty buffer for tokens
    #     dispatched_x = torch.zeros(
    #         self.num_experts * capacity, self.embed_dim, device=x.device, dtype=x.dtype
    #     )
    #
    #     # 3.2. Expand input tokens and routing weights
    #     expanded_x = x.repeat_interleave(self.top_k, dim=0)
    #     flat_routing_weights = routing_weights.view(-1)
    #
    #     # 3.3. Apply capacity mask for tokens and router weights
    #     masked_weights = flat_routing_weights * expert_mask.view(-1, self.num_experts).sum(dim=1)
    #     weighted_x = expanded_x * masked_weights.unsqueeze(-1)
    #
    #     # 3.4. Place tokens in their positions in buffer
    #     dispatched_x.index_add_(0, scatter_indices, weighted_x)
    #     dispatched_x = dispatched_x.view(self.num_experts, capacity, self.embed_dim)
    #
    #     # 4. Run experts and collect outputs
    #     expert_outputs = []
    #     for i in range(self.num_experts):
    #         expert_outputs.append(self.experts[i](dispatched_x[i]))
    #     expert_outputs = torch.stack(expert_outputs)
    #
    #     # 5. Collect results
    #     # 5.1. Flatten results
    #     expert_outputs_flat = expert_outputs.view(-1, self.embed_dim)
    #
    #     # 5.2. Create empty final output
    #     final_output = torch.zeros_like(x, dtype=expert_outputs_flat.dtype, device=expert_outputs_flat.device)
    #
    #     # 5.3. Token index for mapping
    #     token_idx = torch.arange(num_tokens, device=x.device).repeat_interleave(self.top_k)
    #
    #     # 5.4. Create active indices mask
    #     active_indices_mask = expert_mask.view(-1, self.num_experts).sum(dim=1).bool()
    #
    #     # 5.5. Select active results
    #     active_expert_outputs = expert_outputs_flat[scatter_indices[active_indices_mask]]
    #     active_token_destinations = token_idx[active_indices_mask]
    #
    #     # 5.6. Sum experts results with scatter add
    #     final_output.scatter_add_(0, active_token_destinations.unsqueeze(1).expand_as(active_expert_outputs),
    #                               active_expert_outputs)
    #
    #     # 5.7 Transform back to original shape
    #     return final_output.view(*orig_shape)


class GatedMoeFeedForward(MoeFeedForward):
    """Gated Mixture-of-Experts Feed-Forward layer - enable GLU-based activations for MoE"""

    def __init__(
            self,
            embed_dim: int,
            hidden_dim: int,
            num_experts: int,
            activation: nn.Module = nn.SiLU(),
            top_k: int = 1,
            dropout: float = 0.1,
            *args,
            **kwargs
    ):
        super(GatedMoeFeedForward, self).__init__(
            embed_dim=embed_dim,
            hidden_dim=hidden_dim,
            num_experts=num_experts,
            activation=activation,
            top_k=top_k,
            dropout=dropout,
            *args,
            **kwargs
        )

    def _init_experts(self, num_experts: int, embed_dim: int, hidden_dim: int, activation: nn.Module, dropout: float):
        self.experts = nn.ModuleList([
            GatedFeedForward(embed_dim, hidden_dim, activation, dropout)
            for _ in range(num_experts)
        ])
