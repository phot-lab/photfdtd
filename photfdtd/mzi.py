from .waveguide import Waveguide
from .directional_coupler import DirectionalCoupler
from .arc import Arc


class Mzi:
    """ 马赫-曾德干涉仪：由两个方向耦合器（directional coupler）和中间的相移部分组成。用户可以用mmi替换方向耦合器
        gap: 耦合部分上下波导间距
        gap_dc: 方向耦合器耦合部分上下波导间距
        xlength_dc: 方向耦合器的xlength
        ylength_dc: 方向耦合器的ylength
        zlength: 厚度
        couplelength: 耦合长度
        couplelength_dc: 方向耦合器的耦合长度
        addlength_arm1: 上臂额外长度
        addlength_arm2: 下臂额外长度
        x,y,z: 中心坐标
        width: 波导宽度
        refractive_index: 折射率
        background_index: 环境折射率
        name: 名称
        """
    # TODO: 更新MZI的单位，与waveguide一致
    # TODO: Arc被大改之后Mzi也需要更改
    def __init__(self, gap: int = 50, xlength_dc: int = 150, zlength: int = 1, x: int = 350, y: int = 125,
                 z: int = 0, width: int = 20, refractive_index: float = 3.47, name: str = 'mzi', couplelength: int = 100,
                 addlength_arm1: int = 0, addlength_arm2: int = 0, couplelength_dc: int = 10, gap_dc: int = 10, background_index: float = 1.0) -> None:

        self.gap = gap
        self.zlength = zlength
        self.couplelength = couplelength
        self.addlength_arm1 = addlength_arm1
        self.addlength_arm2 = addlength_arm2
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.refractive_index = refractive_index
        self.name = name

        self.gap_dc = gap_dc
        self.xlength_dc = xlength_dc
        self.ylength_dc = self.gap + width * 2
        self.couplelength_dc = couplelength_dc
        self.background_index = background_index



        dc1 = DirectionalCoupler(xlength=self.xlength_dc,
                                 ylength=self.ylength_dc,
                                 zlength=self.zlength,
                                 x=self.x - int(self.couplelength / 2 + self.xlength_dc / 2), # -1是为了防止波导区域重叠报错
                                 y=self.y,
                                 z=self.z,
                                 direction=1,
                                 width=self.width,
                                 name='%s-dc1' % self.name,
                                 refractive_index=self.refractive_index,
                                 xlength_rectangle=self.couplelength_dc,
                                 gap=self.gap_dc,
                                 background_index=self.background_index)
        dc2 = DirectionalCoupler(xlength=self.xlength_dc,
                                 ylength=self.ylength_dc,
                                 zlength=self.zlength,
                                 x=self.x + int(self.couplelength / 2 + self.xlength_dc / 2),
                                 y=self.y,
                                 z=self.z,
                                 direction=1,
                                 width=self.width,
                                 name='%s-dc2' % self.name,
                                 refractive_index=self.refractive_index,
                                 xlength_rectangle=self.couplelength_dc,
                                 gap=self.gap_dc,
                                 background_index=self.background_index)

        outer_radius = int((self.couplelength + 2 * self.width) / 4 + 0.5)

        arc1 = Arc(outer_radius=outer_radius, x=self.x - outer_radius * 2 + self.width,
                   y=self.y + int(self.gap / 2 + 0.5), z=self.z - self.zlength // 2, width=self.width,
                   refractive_index=self.refractive_index, name='%s-arc1' % self.name)
        arc2 = Arc(outer_radius=outer_radius, x=self.x - outer_radius * 2 + self.width,
                   y=self.y - int(self.gap / 2 + 0.5) - outer_radius, z=self.z - self.zlength // 2, width=self.width,
                   refractive_index=self.refractive_index, name='%s-arc2' % self.name)

        arc3 = Arc(outer_radius=outer_radius, x=self.x - outer_radius,
                   y=self.y + int(self.gap / 2 + 0.5) + outer_radius + self.addlength_arm1,
                   z=self.z - self.zlength // 2, width=self.width, refractive_index=self.refractive_index,
                   name='%s-arc3' % self.name)
        arc4 = Arc(outer_radius=outer_radius, x=self.x - outer_radius,
                   y=self.y - int(self.gap / 2 + 0.5) - 2 * outer_radius - self.addlength_arm2,
                   z=self.z - self.zlength // 2, width=self.width, refractive_index=self.refractive_index,
                   name='%s-arc4' % self.name)

        arc5 = Arc(outer_radius=outer_radius, x=self.x,
                   y=self.y + int(self.gap / 2 + 0.5) + outer_radius + self.addlength_arm1,
                   z=self.z - self.zlength // 2, width=self.width, refractive_index=self.refractive_index,
                   name='%s-arc5' % self.name)
        arc6 = Arc(outer_radius=outer_radius, x=self.x,
                   y=self.y - int(self.gap / 2 + 0.5) - 2 * outer_radius - self.addlength_arm2,
                   z=self.z - self.zlength // 2, width=self.width, refractive_index=self.refractive_index,
                   name='%s-arc6' % self.name)

        arc7 = Arc(outer_radius=outer_radius, x=self.x + outer_radius - self.width, y=self.y + int(self.gap / 2 + 0.5),
                   z=self.z - self.zlength // 2, width=self.width, refractive_index=self.refractive_index,
                   name='%s-arc7' % self.name)
        arc8 = Arc(outer_radius=outer_radius, x=self.x + outer_radius - width,
                   y=self.y - int(self.gap / 2 + 0.5) - outer_radius, z=self.z - self.zlength // 2, width=self.width,
                   refractive_index=self.refractive_index, name='%s-arc8' % self.name)

        if self.addlength_arm1 != 0:
            wg1 = Waveguide(xlength=self.width,
                            ylength=self.addlength_arm1,
                            zlength=self.zlength,
                            x=self.x - outer_radius + int(self.width / 2 + 0.5),
                            y=self.y + int(self.gap / 2 + self.addlength_arm1 / 2 + 0.5) + outer_radius,
                            z=self.z,
                            width=self.width,
                            name='%s-waveguide1' % self.name,
                            refractive_index=self.refractive_index,
                            background_index=self.background_index)
            wg2 = Waveguide(xlength=self.width,
                            ylength=self.addlength_arm1,
                            zlength=self.zlength,
                            x=self.x + outer_radius - int(self.width / 2),
                            y=self.y + int(self.gap / 2 + self.addlength_arm1 / 2 + 0.5) + outer_radius,
                            z=self.z,
                            width=self.width,
                            name='%s-waveguide2' % self.name,
                            refractive_index=self.refractive_index,
                            background_index=self.background_index)
        else:
            wg1 = wg2 = 0

        if self.addlength_arm2 != 0:
            wg3 = Waveguide(xlength=self.width,
                            ylength=self.addlength_arm2,
                            zlength=self.zlength,
                            x=self.x - outer_radius + int(self.width / 2),
                            y=self.y - int(self.gap / 2 + self.addlength_arm2 / 2 + 0.5) - outer_radius,
                            z=self.z,
                            width=self.width,
                            name='%s-waveguide3' % self.name,
                            refractive_index=self.refractive_index,
                            background_index=self.background_index)
            wg4 = Waveguide(xlength=self.width,
                            ylength=self.addlength_arm2,
                            zlength=self.zlength,
                            x=self.x + outer_radius - int(self.width / 2),
                            y=self.y - int(self.gap / 2 + self.addlength_arm2 / 2 + 0.5) - outer_radius,
                            z=self.z,
                            width=self.width,
                            name='%s-waveguide4' % self.name,
                            refractive_index=self.refractive_index,
                            background_index=self.background_index)
        else:
            wg3 = wg4 = 0

        self._internal_objects = [arc1, arc2, arc3, arc4, arc5, arc6, arc7, arc8, wg1, wg2, wg3, wg4]
        self._internal_objects.extend(dc1._internal_objects)
        self._internal_objects.extend(dc2._internal_objects)
