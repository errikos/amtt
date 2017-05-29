"""Export functions for Isograph."""
import logging

_logger = logging.getLogger(__name__)


def fmodel_export(ir_container, emitter):
    """Export the failure models from ir_container using the given emitter."""
    for fm in ir_container.failure_models:
        kwargs = dict(name=fm.name, distribution=fm.distribution,
                      remarks=fm.remarks)
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


def manpower_export(ir_container, emitter):
    """Export the manpower (labor) declarations from ir_container."""
    for mp in ir_container.manpower_list:
        emitter.add_labor(identifier=mp.manpower_type,
                          availability=mp.availability,
                          cost=mp.cost)


def spares_export(ir_container, emitter):
    """Export the spares declarations from ir_container."""
    for sp in ir_container.spares_list:
        emitter.add_spare(identifier=sp.device_type,
                          availability=sp.availability,
                          cost=sp.cost)


__all__ = [
    'fmodel_export',
    'manpower_export',
    'spares_export',
]
