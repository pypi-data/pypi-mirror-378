"""Type definitions for MDP components."""

from typing import TypeAlias

from jaxtyping import Array, Float

# State types
StateVector: TypeAlias = Float[Array, "state_dim"]
StateBatch: TypeAlias = Float[Array, "batch_size state_dim"]
StateSpace: TypeAlias = Float[Array, "n_states state_dim"]
BatchedStates: TypeAlias = Float[Array, "n_devices n_batches batch_size state_dim"]

# Action types
ActionVector: TypeAlias = Float[Array, "action_dim"]
ActionSpace: TypeAlias = Float[Array, "n_actions action_dim"]

# Random event types
RandomEventVector: TypeAlias = Float[Array, "event_dim"]
RandomEventSpace: TypeAlias = Float[Array, "n_events event_dim"]

# Value function and policy types
ValueFunction: TypeAlias = Float[Array, "n_states"]
Policy: TypeAlias = Float[Array, "n_states action_dim"]

# Batched computation types
ResultsBatch: TypeAlias = Float[Array, "batch_size"]
BatchedResults: TypeAlias = Float[Array, "n_devices n_batches batch_size"]

# Other types
Reward: TypeAlias = float
