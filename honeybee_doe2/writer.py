from .properties.inputils import blocks as fb
from .properties.inputils.compliance import ComplianceData
from .properties.inputils.sitebldg import SiteBldgData as sbd
from .properties.inputils.run_period import RunPeriod
from .properties.inputils.title import Title
from .properties.inputils.glass_types import GlassType

from honeybee.model import Model
from honeybee_energy.construction.window import WindowConstruction


def model_to_inp(hb_model):
    # type: (Model) -> str
    rp = RunPeriod()
    comp_data = ComplianceData()
    sb_data = sbd()

    hb_model.convert_to_units(units='Feet')
    # TODO: Add routine to 'reverbose' constr/matters prior to writing to inp
    window_constructions = []
    for construction in hb_model.properties.energy.constructions:
        if isinstance(construction, WindowConstruction):
            window_constructions.append(GlassType.from_hb_window_constr(construction))

    data = [
        hb_model.properties.doe2._header,
        fb.global_params,
        fb.ttrpddh,
        Title(title=str(hb_model.display_name)).to_inp(),
        rp.to_inp(),  # TODO unhardcode
        fb.comply,
        comp_data.to_inp(),
        sb_data.to_inp(),
        fb.mats_layers,
        hb_model.properties.doe2.mats_cons_layers,
        fb.glzCode,
        '\n'.join(gt.to_inp() for gt in window_constructions),
        fb.polygons,
        '\n'.join(s.story_poly for s in hb_model.properties.doe2.stories),
        fb.wallParams,
        # '\n'.join(shd.to_inp() for shd in hb_model.context_shades),  # TODO shade support
        fb.miscCost,
        fb.perfCurve,
        fb.floorNspace,
        '\n'.join(str(story) for story in hb_model.properties.doe2.stories),
        fb.elecFuelMeter,
        fb.elec_meter,
        fb.fuel_meter,
        fb.master_meter,
        fb.hvac_circ_loop,
        fb.pumps,
        fb.heat_exch,
        fb.circ_loop,
        fb.chiller_objs,
        fb.boiler_objs,
        fb.dwh,
        fb.heat_reject,
        fb.tower_free,
        fb.pvmod,
        fb.elecgen,
        fb.thermal_store,
        fb.ground_loop_hx,
        fb.comp_dhw_res,
        fb.steam_cld_mtr,
        fb.steam_mtr,
        fb.chill_meter,
        fb.hvac_sys_zone,
        # '\n'.join(hv_sys.to_inp()
        # for hv_sys in hb_model.hvac_system_zone),  # TODO need to frame up hvac
        fb.misc_meter_hvac,
        fb.equip_controls,
        fb.load_manage,
        fb.big_util_rate,
        fb.ratchets,
        fb.block_charge,
        fb.small_util_rate,
        fb.output_reporting,
        fb.loads_non_hrly,
        fb.sys_non_hrly,
        fb.plant_non_hrly,
        fb.econ_non_hrly,
        fb.hourly_rep,
        fb.the_end
    ]
    return str('\n\n'.join(data))
