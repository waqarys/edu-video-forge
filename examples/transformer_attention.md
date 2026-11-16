# Transformer Attention Mechanism

## Scene: chalkboard
**Narration:** Attention allows the model to focus on relevant parts of the input when producing each output token.
**Content:**
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V

## Scene: webgl
**Narration:** Imagine query, key, and value vectors interacting in a high-dimensional space.
**Content:**
Three.js visualization of multi-head attention (rotating attention heads)

## Scene: code
**Narration:** A minimal PyTorch-style attention implementation.
**Content:**
```python
def scaled_dot_product_attention(Q, K, V):
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    attn = F.softmax(scores, dim=-1)
    return torch.matmul(attn, V)
```
