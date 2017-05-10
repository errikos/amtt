"""Exports the failure models for Isograph."""
import logging

_logger = logging.getLogger(__name__)


def fm_export(ir_container, emitter):
    """Export the failure models from ir_container using the given emitter."""
    for fm in ir_container.failure_models:
        kwargs = dict(name=fm.name, distribution=fm.distribution)
        # Obtain the appropriate parameters for each distribution
        if fm.distribution.lower() == 'exponential':
            kwargs.update(mttf=fm.parameters[0])
        if fm.distribution.lower() in ['weibull', 'bi-weibull', 'tri-weibull']:
            beta1, eta1, gamma1 = fm.parameters[0]
            kwargs.update(beta1=beta1, eta1=eta1, gamma1=gamma1)
        if fm.distribution.lower() in ['bi-weibull', 'tri-weibull']:
            beta2, eta2, gamma2 = fm.parameters[1]
            kwargs.update(beta2=beta2, eta2=eta2, gamma2=gamma2)
        if fm.distribution.lower in ['tri-weibull']:
            beta3, eta3, gamma3 = fm.parameters[2]
            kwargs.update(beta3=beta3, eta3=eta3, gamma3=gamma3)
        # Register the failure model with the emitter
        emitter.add_failure_model(**kwargs)
