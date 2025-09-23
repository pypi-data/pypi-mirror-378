import torch
from cvvdp_metric import cvvdp

import logging

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)

metric = cvvdp(display_name='standard_4k', config_paths=["../metric_configs/cvvdp_overconstancy_transd/cvvdp_parameters.json"])

device = metric.device

sz = (4, 10, 1024, 1024)

with torch.autograd.detect_anomaly():
    for kk in range(100):

        #        "mask_p": { "value": "default", "range":  [2, 3], "clamp": "hard" },
        #        "mask_q": { "value": "default", "range": [1, 2.4], "clamp": "hard" }, 
        #        "xcm_weights": { "value": "default", "range": [-10, 2] }

        metric.mask_p = torch.rand((1), device=device, requires_grad=True)+2
        metric.mask_q = torch.rand((4), device=device, requires_grad=True)*1.4+1
        metric.xcm_weights = torch.rand((4,4), device=device, requires_grad=True)*12-10

        T = torch.randn( sz, device=device )*1
        R = torch.randn( sz, device=device )*1
        S = torch.exp( torch.randn( sz, device=device )*5+3 )

        D = metric.apply_masking_model( T, R, S )

        D_all = D.sum()
        D_all.backward()

        if D.isnan().any() or D.isinf().any():
            print( "Masking produces NaN or Inf values" )
        else:
            print( "No NaN or Inf values found. Huray!" )

    


