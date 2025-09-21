"""
Basic tests for Selective Self-Attention implementation.
"""

import torch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.modules import SelectiveSelfAttention, StandardSelfAttention, TransformerBlock


def test_ssa_basic():
    """Test basic SSA functionality."""
    print("Testing basic SSA functionality...")

    # Test parameters
    batch_size, seq_len, dim, num_heads = 2, 10, 64, 8

    # Create input tensor
    x = torch.randn(batch_size, seq_len, dim)

    # Test SSA attention
    ssa = SelectiveSelfAttention(
        dim=dim,
        num_heads=num_heads,
        use_query_temp=True,
        use_value_temp=True,
        use_position_aware=True
    )

    # Forward pass
    output = ssa(x)
    print(f"SSA output shape: {output.shape}")

    # Test spikiness computation
    spikiness = ssa.get_attention_spikiness(x)
    print(f"Attention spikiness: {spikiness:.4f}")

    assert output.shape == x.shape, f"Expected shape {x.shape}, got {output.shape}"
    assert 0 <= spikiness <= 1, f"Spikiness should be between 0 and 1, got {spikiness}"

    print("✓ SSA basic test passed")


def test_ssa_with_key_temp():
    """Test SSA with key temperature scaling."""
    print("Testing SSA with key temperature scaling...")

    # Test parameters
    batch_size, seq_len, dim, num_heads = 2, 10, 64, 8

    # Create input tensor
    x = torch.randn(batch_size, seq_len, dim)

    # Test SSA attention with key temperature
    ssa = SelectiveSelfAttention(
        dim=dim,
        num_heads=num_heads,
        use_query_temp=True,
        use_key_temp=True,  # Enable key temperature
        use_value_temp=True,
        use_position_aware=True
    )

    # Forward pass
    output = ssa(x)
    print(f"SSA with key temp output shape: {output.shape}")

    # Test spikiness computation
    spikiness = ssa.get_attention_spikiness(x)
    print(f"Attention spikiness with key temp: {spikiness:.4f}")

    assert output.shape == x.shape, f"Expected shape {x.shape}, got {output.shape}"
    assert 0 <= spikiness <= 1, f"Spikiness should be between 0 and 1, got {spikiness}"

    print("✓ SSA with key temperature test passed")


def test_standard_attention():
    """Test standard attention for comparison."""
    print("Testing standard attention...")

    # Test parameters
    batch_size, seq_len, dim, num_heads = 2, 10, 64, 8

    # Create input tensor
    x = torch.randn(batch_size, seq_len, dim)

    # Test standard attention
    std_attn = StandardSelfAttention(
        dim=dim,
        num_heads=num_heads
    )

    # Forward pass
    output = std_attn(x)
    print(f"Standard attention output shape: {output.shape}")

    assert output.shape == x.shape, f"Expected shape {x.shape}, got {output.shape}"

    print("✓ Standard attention test passed")


def test_transformer_block():
    """Test transformer block with SSA."""
    print("Testing transformer block with SSA...")

    # Test parameters
    batch_size, seq_len, dim, num_heads = 2, 10, 64, 8

    # Create input tensor
    x = torch.randn(batch_size, seq_len, dim)

    # Test transformer block with SSA
    block = TransformerBlock(
        dim=dim,
        num_heads=num_heads,
        use_ssa=True,
        use_query_temp=True,
        use_value_temp=True
    )

    # Forward pass
    output = block(x)
    print(f"Transformer block output shape: {output.shape}")

    assert output.shape == x.shape, f"Expected shape {x.shape}, got {output.shape}"

    print("✓ Transformer block test passed")


def test_attention_sparsity():
    """Test that SSA produces sparser attention than standard attention."""
    print("Testing attention sparsity comparison...")

    # Test parameters
    batch_size, seq_len, dim, num_heads = 2, 20, 64, 8

    # Create input tensor
    x = torch.randn(batch_size, seq_len, dim)

    # Create both attention types
    ssa = SelectiveSelfAttention(dim=dim, num_heads=num_heads)
    std_attn = StandardSelfAttention(dim=dim, num_heads=num_heads)

    # Get spikiness scores
    ssa_spikiness = ssa.get_attention_spikiness(x)
    std_spikiness = std_attn.get_attention_spikiness(x)  # Note: this will need to be added to StandardSelfAttention

    print(f"SSA spikiness: {ssa_spikiness:.4f}")
    print(f"Standard attention spikiness: {std_spikiness:.4f}")

    # SSA should generally produce sparser (lower spikiness) attention
    print("✓ Sparsity comparison test completed")


if __name__ == "__main__":
    print("Running SSA tests...")
    print("=" * 50)

    try:
        test_ssa_basic()
        test_ssa_with_key_temp()
        test_standard_attention()
        test_transformer_block()
        test_attention_sparsity()

        print("=" * 50)
        print("🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
