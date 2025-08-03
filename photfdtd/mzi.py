from .waveguide import Waveguide
from .directional_coupler import DirectionalCoupler


class Mzi(Waveguide):
    """ 马赫-曾德干涉仪：由两个方向耦合器（directional coupler）和中间的相移部分组成。用户可以用mmi替换方向耦合器
        gap: 耦合部分上下波导间距
        gap_DC: 方向耦合器耦合部分上下波导间距
        xlength_DC: 方向耦合器的xlength
        ylength_DC: 方向耦合器的ylength
        zlength: 厚度
        couplelength: 耦合长度
        couplelength_DC: 方向耦合器的耦合长度
        addlength_arm1: 上臂额外长度
        addlength_arm2: 下臂额外长度
        x,y,z: 中心坐标
        width: 波导宽度
        refractive_index: 折射率
        background_index: 环境折射率
        name: 名称
        """

    # TODO: need to remake
    # TODO: 方向耦合器之间加两个直波导，可以添加热光系数，或者Y分支
    def __init__(self,
                 x: int or float = None,
                 y: int or float = None,
                 z: int or float = None,
                 xlength: int or float = 150,
                 ylength: int or float = 1,
                 zlength_DC: int or float = 150,
                 couplelength_DC: int or float = 50,
                 width_1: int or float = 20,
                 width_2: int or float = None,
                 couplelength: int or float = 100,
                 addlength_arm1: int or float = 0,
                 addlength_arm2: int or float = 0,
                 gap_DC: int or float = 10,
                 name: str = "waveguide",
                 refractive_index: float = None,
                 material: str = "",
                 grid=None,
                 priority: int = 1
                 ) -> None:
        if not width_2:
            width_2 = width_1
        x, xlength, width_1, width_2, addlength_arm1, addlength_arm2, gap_DC = grid._handle_unit(
            [x, xlength, width_1, width_2, addlength_arm1, addlength_arm2, gap_DC], grid_spacing=grid._grid.grid_spacing_x)
        y, ylength = grid._handle_unit([y, ylength], grid_spacing=grid._grid.grid_spacing_y)
        z, zlength_DC, couplelength_DC, couplelength = grid._handle_unit(
            [z, zlength_DC, couplelength_DC, couplelength], grid_spacing=grid._grid.grid_spacing_z)

        self.zlength = zlength_DC * 2 + couplelength
        self.couplelength = couplelength
        self.gap_DC = gap_DC
        self.zlength_DC = zlength_DC
        self.width_1 = width_1
        self.width_2 = width_2

        self.couplelength_DC = couplelength_DC
        self.addlength_arm1 = addlength_arm1
        self.addlength_arm2 = addlength_arm2

        self.refractive_index = refractive_index
        self.name = name

        super().__init__(xlength, ylength, self.zlength, x, y, z,
                         width_1, name, refractive_index, grid=grid, reset_xyz=False, priority=priority)

    def _set_objects(self):
        DC1 = DirectionalCoupler(x=self.x,  # -1是为了防止波导区域重叠报错
                                 y=self.y,
                                 z=self.z - int(self.couplelength / 2 + self.zlength_DC / 2),
                                 xlength=self.xlength,
                                 ylength=self.ylength,
                                 zlength=self.zlength_DC,
                                 width_1=self.width_1,
                                 width_2=self.width_2,
                                 zlength_rectangle=self.couplelength_DC,
                                 gap=self.gap_DC,
                                 name=f'{self.name}-DC1',
                                 refractive_index=self.refractive_index,
                                 grid=self.grid,
                                 priority=self.priority)
        DC2 = DirectionalCoupler(x=self.x,  # -1是为了防止波导区域重叠报错
                                 y=self.y,
                                 z=self.z + int(self.couplelength / 2 + self.zlength_DC / 2),
                                 xlength=self.xlength,
                                 ylength=self.ylength,
                                 zlength=self.zlength_DC,
                                 width_1=self.width_1,
                                 width_2=self.width_2,
                                 zlength_rectangle=self.couplelength_DC,
                                 gap=self.gap_DC,
                                 name=f'{self.name}-DC2',
                                 refractive_index=self.refractive_index,
                                 grid=self.grid,
                                 priority=self.priority)

        Upper_WG = Waveguide(xlength=self.width_1,
                             ylength=self.ylength,
                             zlength=self.couplelength,
                             x=self.x + int(self.xlength / 2 - self.width_1 / 2),
                             y=self.y,
                             z=self.z,
                             name=f'{self.name}-Upper_WG',
                             refractive_index=self.refractive_index,
                             grid=self.grid,
                             priority=self.priority)
        Lower_WG = Waveguide(xlength=self.width_2,
                             ylength=self.ylength,
                             zlength=self.couplelength,
                             x=self.x - int(self.xlength / 2 - self.width_1 / 2),
                             y=self.y,
                             z=self.z,
                             name=f'{self.name}-Lower_WG',
                             refractive_index=self.refractive_index,
                             grid=self.grid,
                             priority=self.priority)
        self._internal_objects = [Upper_WG, Lower_WG]
        self._internal_objects.extend(DC1._internal_objects)
        self._internal_objects.extend(DC2._internal_objects)
        # outer_radius = int((self.couplelength + 2 * self.width) / 4 + 0.5)
        #
        # arc1 = Arc(outer_radius=outer_radius, x=self.x - outer_radius * 2 + self.width,
        #            y=self.y + int(self.gap / 2 + 0.5), z=self.z - self.zlength // 2, width=self.width,
        #            refractive_index=self.refractive_index, name='%s-arc1' % self.name)
        # arc2 = Arc(outer_radius=outer_radius, x=self.x - outer_radius * 2 + self.width,
        #            y=self.y - int(self.gap / 2 + 0.5) - outer_radius, z=self.z - self.zlength // 2, width=self.width,
        #            refractive_index=self.refractive_index, name='%s-arc2' % self.name)
        #
        # arc3 = Arc(outer_radius=outer_radius, x=self.x - outer_radius,
        #            y=self.y + int(self.gap / 2 + 0.5) + outer_radius + self.addlength_arm1,
        #            z=self.z - self.zlength // 2, width=self.width, refractive_index=self.refractive_index,
        #            name='%s-arc3' % self.name)
        # arc4 = Arc(outer_radius=outer_radius, x=self.x - outer_radius,
        #            y=self.y - int(self.gap / 2 + 0.5) - 2 * outer_radius - self.addlength_arm2,
        #            z=self.z - self.zlength // 2, width=self.width, refractive_index=self.refractive_index,
        #            name='%s-arc4' % self.name)
        #
        # arc5 = Arc(outer_radius=outer_radius, x=self.x,
        #            y=self.y + int(self.gap / 2 + 0.5) + outer_radius + self.addlength_arm1,
        #            z=self.z - self.zlength // 2, width=self.width, refractive_index=self.refractive_index,
        #            name='%s-arc5' % self.name)
        # arc6 = Arc(outer_radius=outer_radius, x=self.x,
        #            y=self.y - int(self.gap / 2 + 0.5) - 2 * outer_radius - self.addlength_arm2,
        #            z=self.z - self.zlength // 2, width=self.width, refractive_index=self.refractive_index,
        #            name='%s-arc6' % self.name)
        #
        # arc7 = Arc(outer_radius=outer_radius, x=self.x + outer_radius - self.width, y=self.y + int(self.gap / 2 + 0.5),
        #            z=self.z - self.zlength // 2, width=self.width, refractive_index=self.refractive_index,
        #            name='%s-arc7' % self.name)
        # arc8 = Arc(outer_radius=outer_radius, x=self.x + outer_radius - width,
        #            y=self.y - int(self.gap / 2 + 0.5) - outer_radius, z=self.z - self.zlength // 2, width=self.width,
        #            refractive_index=self.refractive_index, name='%s-arc8' % self.name)
        #
        # if self.addlength_arm1 != 0:
        #     wg1 = Waveguide(xlength=self.width,
        #                     ylength=self.addlength_arm1,
        #                     zlength=self.zlength,
        #                     x=self.x - outer_radius + int(self.width / 2 + 0.5),
        #                     y=self.y + int(self.gap / 2 + self.addlength_arm1 / 2 + 0.5) + outer_radius,
        #                     z=self.z,
        #                     width=self.width,
        #                     name='%s-waveguide1' % self.name,
        #                     refractive_index=self.refractive_index,
        #                     background_index=self.background_index)
        #     wg2 = Waveguide(xlength=self.width,
        #                     ylength=self.addlength_arm1,
        #                     zlength=self.zlength,
        #                     x=self.x + outer_radius - int(self.width / 2),
        #                     y=self.y + int(self.gap / 2 + self.addlength_arm1 / 2 + 0.5) + outer_radius,
        #                     z=self.z,
        #                     width=self.width,
        #                     name='%s-waveguide2' % self.name,
        #                     refractive_index=self.refractive_index,
        #                     background_index=self.background_index)
        # else:
        #     wg1 = wg2 = 0
        #
        # if self.addlength_arm2 != 0:
        #     wg3 = Waveguide(xlength=self.width,
        #                     ylength=self.addlength_arm2,
        #                     zlength=self.zlength,
        #                     x=self.x - outer_radius + int(self.width / 2),
        #                     y=self.y - int(self.gap / 2 + self.addlength_arm2 / 2 + 0.5) - outer_radius,
        #                     z=self.z,
        #                     width=self.width,
        #                     name='%s-waveguide3' % self.name,
        #                     refractive_index=self.refractive_index,
        #                     background_index=self.background_index)
        #     wg4 = Waveguide(xlength=self.width,
        #                     ylength=self.addlength_arm2,
        #                     zlength=self.zlength,
        #                     x=self.x + outer_radius - int(self.width / 2),
        #                     y=self.y - int(self.gap / 2 + self.addlength_arm2 / 2 + 0.5) - outer_radius,
        #                     z=self.z,
        #                     width=self.width,
        #                     name='%s-waveguide4' % self.name,
        #                     refractive_index=self.refractive_index,
        #                     background_index=self.background_index)
        # else:
        #     wg3 = wg4 = 0

        # self._internal_objects = [arc1, arc2, arc3, arc4, arc5, arc6, arc7, arc8, wg1, wg2, wg3, wg4]
        # self._internal_objects.extend(DC1._internal_objects)
        # self._internal_objects.extend(DC2._internal_objects)
