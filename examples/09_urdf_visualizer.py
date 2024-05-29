"""Robot URDF visualizer

Requires yourdfpy and robot_descriptions. Any URDF supported by yourdfpy should work.
- https://github.com/robot-descriptions/robot_descriptions.py
- https://github.com/clemense/yourdfpy

The :class:`viser.extras.ViserUrdf` is a lightweight interface between yourdfpy
and viser. It can also take a path to a local URDF file as input.
"""

from __future__ import annotations

import time

import numpy as onp
import tyro
from robot_descriptions.loaders.yourdfpy import load_robot_description

import viser
from viser.extras import ViserUrdf


def main() -> None:
    # Start viser server.
    server = viser.ViserServer()

    # Logic for updating the visualized robot.
    gui_joints: list[viser.GuiInputHandle[float]] = []
    initial_angles: list[float] = []

    def update_robot_model(robot_name: str) -> None:
        server.scene.reset()

        loading_modal = server.gui.add_modal("Loading URDF...")
        with loading_modal:
            server.gui.add_markdown("See terminal for progress!")

        # Create a helper for adding URDFs to Viser. This just adds meshes to the scene,
        # helps us set the joint angles, etc.
        urdf = ViserUrdf(
            server,
            # This can also be set to a path to a local URDF file.
            urdf_or_path=load_robot_description(robot_name),
        )
        loading_modal.close()

        for gui_joint in gui_joints:
            gui_joint.remove()
        gui_joints.clear()

        for joint_name, (lower, upper) in urdf.get_actuated_joint_limits().items():
            lower = lower if lower is not None else -onp.pi
            upper = upper if upper is not None else onp.pi

            initial_angle = 0.0 if lower < 0 and upper > 0 else (lower + upper) / 2.0
            slider = server.gui.add_slider(
                label=joint_name,
                min=lower,
                max=upper,
                step=1e-3,
                initial_value=initial_angle,
            )
            slider.on_update(  # When sliders move, we update the URDF configuration.
                lambda _: urdf.update_cfg(onp.array([gui.value for gui in gui_joints]))
            )

            gui_joints.append(slider)
            initial_angles.append(initial_angle)

        # Apply initial joint angles.
        urdf.update_cfg(onp.array([gui.value for gui in gui_joints]))

    robot_model_name = server.gui.add_dropdown("Robot model", ROBOT_MODEL_LIST)
    robot_model_name.on_update(lambda _: update_robot_model(robot_model_name.value))

    # Create joint reset button.
    reset_button = server.gui.add_button("Reset")

    @reset_button.on_click
    def _(_):
        for g, initial_angle in zip(gui_joints, initial_angles):
            g.value = initial_angle

    while True:
        time.sleep(10.0)


ROBOT_MODEL_LIST = (
    "edo_description",
    "fanuc_m710ic_description",
    "gen2_description",
    "gen3_description",
    "iiwa14_description",
    "iiwa7_description",
    "panda_description",
    "poppy_ergo_jr_description",
    "ur10_description",
    "ur3_description",
    "ur5_description",
    "z1_description",
    "bolt_description",
    "cassie_description",
    "rhea_description",
    "spryped_description",
    "upkie_description",
    "baxter_description",
    "nextage_description",
    "poppy_torso_description",
    "yumi_description",
    "cf2_description",
    "skydio_x2_description",
    "double_pendulum_description",
    "finger_edu_description",
    "simple_humanoid_description",
    "trifinger_edu_description",
    "allegro_hand_description",
    "barrett_hand_description",
    "robotiq_2f85_description",
    "atlas_drc_description",
    "atlas_v4_description",
    "draco3_description",
    "ergocub_description",
    "g1_description",
    "h1_description",
    "icub_description",
    "jaxon_description",
    "jvrc_description",
    "r2_description",
    "romeo_description",
    "sigmaban_description",
    "talos_description",
    "valkyrie_description",
    "a1_description",
    "aliengo_description",
    "anymal_b_description",
    "anymal_c_description",
    "b1_description",
    "go1_description",
    "go2_description",
    "hyq_description",
    "laikago_description",
    "mini_cheetah_description",
    "minitaur_description",
    "solo_description",
)

if __name__ == "__main__":
    tyro.cli(main)
