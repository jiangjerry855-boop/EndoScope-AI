"""Compact U-Net baseline, trained from scratch (not the original U-Net)."""
import torch
from torch import nn
import torch.nn.functional as F


class Block(nn.Sequential):
    def __init__(self, incoming, outgoing):
        super().__init__(
            nn.Conv2d(incoming, outgoing, 3, padding=1, bias=False),
            nn.GroupNorm(4, outgoing), nn.SiLU(inplace=True),
            nn.Conv2d(outgoing, outgoing, 3, padding=1, bias=False),
            nn.GroupNorm(4, outgoing), nn.SiLU(inplace=True),
        )


class CompactUNet(nn.Module):
    def __init__(self, base=12):
        super().__init__()
        self.e1 = Block(3, base)
        self.e2 = Block(base, base * 2)
        self.e3 = Block(base * 2, base * 4)
        self.mid = Block(base * 4, base * 8)
        self.d3 = Block(base * 12, base * 4)
        self.d2 = Block(base * 6, base * 2)
        self.d1 = Block(base * 3, base)
        self.out = nn.Conv2d(base, 1, 1)

    def forward(self, x):
        a = self.e1(x)
        b = self.e2(F.max_pool2d(a, 2))
        c = self.e3(F.max_pool2d(b, 2))
        z = self.mid(F.max_pool2d(c, 2))
        z = self.d3(torch.cat([F.interpolate(z, size=c.shape[2:], mode="bilinear", align_corners=False), c], 1))
        z = self.d2(torch.cat([F.interpolate(z, size=b.shape[2:], mode="bilinear", align_corners=False), b], 1))
        z = self.d1(torch.cat([F.interpolate(z, size=a.shape[2:], mode="bilinear", align_corners=False), a], 1))
        return self.out(z)
