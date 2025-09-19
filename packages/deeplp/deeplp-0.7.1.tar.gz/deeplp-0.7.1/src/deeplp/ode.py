import torch


def createPhi(
    D=None,
    A=None,
    b=None,
    *,
    model: str = "pinn",
):
    assert A is not None, "A must be defined"
    _, n = A.shape
    if model == "pinn":
        if b is None:

            def makePhiWithb(b):
                b = b.t()

                def phi(y):
                    y = y.unsqueeze(0) if y.dim() == 1 else y
                    # Batched input: y shape: (B, n + r)
                    x = y[:, :n]  # (B, n)
                    u = y[:, n:]  # (B, r)
                    # Make b broadcastable: shape (1, r)
                    # b_flat = b
                    m = torch.clamp(u + torch.matmul(x, A.t()) - b, min=0.0)  # (B, r)
                    top = -(D.unsqueeze(0) + torch.matmul(m, A))  # (B, n)
                    bottom = m - u  # (B, r)
                    return torch.cat((top, bottom), dim=1)

                return phi

            return makePhiWithb
        else:
            b = b.t()

            def makePhiWithD(D):
                def phi(y):
                    y = y.unsqueeze(0) if y.dim() == 1 else y
                    x = y[:, :n]  # (B, n)
                    u = y[:, n:]  # (B, r)
                    m = torch.clamp(u + torch.matmul(x, A.t()) - b, min=0.0)  # (B, r)
                    top = -(D.unsqueeze(0) + torch.matmul(m, A))  # (B, n)
                    bottom = m - u  # (B, r)
                    return torch.cat((top, bottom), dim=1)

                return phi

            return makePhiWithD
    else:
        if b is None:

            def makePhiWithb(b):
                b = b.unsqueeze(0) if b.dim() == 1 else b
                b = b.t()

                def phi(y):
                    y = y.unsqueeze(0) if y.dim() == 1 else y
                    rows, _ = y.shape
                    x = y[:, :n]  # shape: (n,)
                    u = y[:, n : n + n]  # shape: (1,)
                    v = y[:, n + n :]  # shape: (1,)
                    eq1_part1 = (D - 0.5 * (u**2)).t()
                    Eq1 = eq1_part1 + A.t() @ v.t()
                    Eq2 = (u * x).t()
                    Eq3 = A @ x.t() - b
                    return -torch.cat((Eq1, Eq2, Eq3), dim=0).view(rows, -1)

                return phi

            return makePhiWithb
        else:
            b = b.unsqueeze(0) if b.dim() == 1 else b
            b = b.t()

            def makePhiWithD(D):

                def phi(y):
                    y = y.unsqueeze(0) if y.dim() == 1 else y
                    rows, _ = y.shape
                    x = y[:, :n]  # shape: (n,)
                    u = y[:, n : n + n]  # shape: (1,)
                    v = y[:, n + n :]  # shape: (1,)
                    eq1_part1 = (D - 0.5 * (u**2)).t()
                    Eq1 = eq1_part1 + A.t() @ v.t()
                    Eq2 = (u * x).t()
                    Eq3 = A @ x.t() - b
                    return -torch.cat((Eq1, Eq2, Eq3), dim=0).view(rows, -1)

                return phi

        return makePhiWithD


# def createPhi2(D, A):
#     _, n = A.shape

#     def makePhiWithb(b):
#         b = b.t()

#         def phi(y):
#             y = y.unsqueeze(0) if y.dim() == 1 else y
#             rows, _ = y.shape
#             x = y[:, :n]  # shape: (n,)
#             u = y[:, n : n + n]  # shape: (1,)
#             v = y[:, n + n :]  # shape: (1,)
#             eq1_part1 = (D - 0.5 * (u**2)).t()
#             Eq1 = eq1_part1 + A.t() @ v.t()
#             Eq2 = (u * x).t()
#             Eq3 = A @ x.t() - b
#             # # Concatenate along dimension 0 to form a (n+1, 1) tensor, then flatten to 1D
#             return torch.cat((Eq1, Eq2, Eq3), dim=0).view(rows, -1)

#         return phi

#     return makePhiWithb


def createObjectiveFun(D):
    n = len(D)

    def object_fun(y):
        y = y.unsqueeze(0) if y.dim() == 1 else y
        x = y[:, :n]  # shape: (B, n)
        return (x * D).sum(dim=1)

    return object_fun


# def createDPhi(A, b):
#     r, n = A.shape

#     def makePhiWithD(D):
#         def phi1(y):
#             if y.dim() == 1:
#                 # y is a single sample: shape (n+1,)
#                 x = y[:n]  # shape: (n,)
#                 u = y[n:]  # shape: (1,)
#                 u = u.unsqueeze(1)  # shape: (1,1)
#                 x_unsq = x.unsqueeze(0)  # shape: (1,n)
#                 # Use matmul: (1,n) @ (n,1) -> (1,1)
#                 m = torch.clamp(
#                     u + torch.matmul(x_unsq, A.t()) - b, min=0.0
#                 )  # shape: (1,1)
#                 top = -(
#                     D.unsqueeze(1) + torch.matmul(A.t(), m)
#                 )  # D.unsqueeze(1): (n,1), A.t(): (n,1), m: (1,1)
#                 bottom = m - u  # shape: (1,1)
#                 # Concatenate along dimension 0 to form a (n+1, 1) tensor, then flatten to 1D
#                 return torch.cat((top, bottom), dim=0).view(-1)
#             elif y.dim() == 2:
#                 # Batched input: y shape: (B, n+1)
#                 x = y[:, :n]  # shape: (B, n)
#                 u = y[:, n:]  # shape: (B, 1)
#                 # Compute batched multiplication: (B, n) @ (n, 1) -> (B, 1)
#                 m = torch.clamp(u + torch.matmul(x, A.t()) - b, min=0.0)  # shape: (B,1)
#                 # Compute top: we want for each sample: top[i] = -(D.unsqueeze(1) + A.t() @ m[i])
#                 # Instead, we do: (B,1) @ (1, n) = (B, n) and add D (unsqueezed to (1,n))
#                 top = -(D.unsqueeze(0) + torch.matmul(m, A))  # shape: (B, n)
#                 bottom = m - u  # shape: (B, 1)
#                 # Concatenate along dim=1 to yield (B, n+1)
#                 return torch.cat((top, bottom), dim=1)

#         def phi2(y):
#             # This branch is used when r != 1.
#             if y.dim() == 1:
#                 # Single sample: y shape: (n + r,)
#                 x = y[:n]  # (n,)
#                 u = y[n:]  # (r,)
#                 b_flat = b.view(-1)  # (r,)
#                 m = torch.clamp(u + A @ x - b_flat, min=0.0)  # (r,)
#                 top = -(D + A.t() @ m)  # (n,)
#                 bottom = m - u  # (r,)
#                 return torch.cat((top, bottom), 0)
#             elif y.dim() == 2:
#                 # Batched input: y shape: (B, n + r)
#                 x = y[:, :n]  # (B, n)
#                 u = y[:, n:]  # (B, r)
#                 # Make b broadcastable: shape (1, r)
#                 b_flat = b.view(1, -1)
#                 m = torch.clamp(u + torch.matmul(x, A.t()) - b_flat, min=0.0)  # (B, r)
#                 top = -(D.unsqueeze(0) + torch.matmul(m, A))  # (B, n)
#                 bottom = m - u  # (B, r)
#                 return torch.cat((top, bottom), dim=1)

#         phi = phi1 if r == 1 else phi2
#         return phi

#     return makePhiWithD


# def createPhi(D, A):
#     r, n = A.shape

#     def makePhiWithb(b):
#         def phi1(y):
#             if y.dim() == 1:
#                 # y is a single sample: shape (n+1,)
#                 x = y[:n]  # shape: (n,)
#                 u = y[n:]  # shape: (1,)
#                 u = u.unsqueeze(1)  # shape: (1,1)
#                 x_unsq = x.unsqueeze(0)  # shape: (1,n)
#                 # Use matmul: (1,n) @ (n,1) -> (1,1)
#                 m = torch.clamp(
#                     u + torch.matmul(x_unsq, A.t()) - b, min=0.0
#                 )  # shape: (1,1)
#                 top = -(
#                     D.unsqueeze(1) + torch.matmul(A.t(), m)
#                 )  # D.unsqueeze(1): (n,1), A.t(): (n,1), m: (1,1)
#                 bottom = m - u  # shape: (1,1)
#                 # Concatenate along dimension 0 to form a (n+1, 1) tensor, then flatten to 1D
#                 return torch.cat((top, bottom), dim=0).view(-1)
#             elif y.dim() == 2:
#                 # Batched input: y shape: (B, n+1)
#                 x = y[:, :n]  # shape: (B, n)
#                 u = y[:, n:]  # shape: (B, 1)
#                 # Compute batched multiplication: (B, n) @ (n, 1) -> (B, 1)
#                 m = torch.clamp(u + torch.matmul(x, A.t()) - b, min=0.0)  # shape: (B,1)
#                 # Compute top: we want for each sample: top[i] = -(D.unsqueeze(1) + A.t() @ m[i])
#                 # Instead, we do: (B,1) @ (1, n) = (B, n) and add D (unsqueezed to (1,n))
#                 top = -(D.unsqueeze(0) + torch.matmul(m, A))  # shape: (B, n)
#                 bottom = m - u  # shape: (B, 1)
#                 # Concatenate along dim=1 to yield (B, n+1)
#                 return torch.cat((top, bottom), dim=1)

#         def phi2(y):
#             # This branch is used when r != 1.
#             if y.dim() == 1:
#                 # Single sample: y shape: (n + r,)
#                 x = y[:n]  # (n,)
#                 u = y[n:]  # (r,)
#                 b_flat = b.view(-1)  # (r,)
#                 m = torch.clamp(u + A @ x - b_flat, min=0.0)  # (r,)
#                 top = -(D + A.t() @ m)  # (n,)
#                 bottom = m - u  # (r,)
#                 return torch.cat((top, bottom), 0)
#             elif y.dim() == 2:
#                 # Batched input: y shape: (B, n + r)
#                 x = y[:, :n]  # (B, n)
#                 u = y[:, n:]  # (B, r)
#                 # Make b broadcastable: shape (1, r)
#                 b_flat = b.view(1, -1)
#                 m = torch.clamp(u + torch.matmul(x, A.t()) - b_flat, min=0.0)  # (B, r)
#                 top = -(D.unsqueeze(0) + torch.matmul(m, A))  # (B, n)
#                 bottom = m - u  # (B, r)
#                 return torch.cat((top, bottom), dim=1)

#         phi = phi1 if r == 1 else phi2
#         return phi

#     return makePhiWithb
