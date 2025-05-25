from .core import *

class SimulationOptions:
	"""
	Option set for AWG simulations.AWG仿真选项设置。
	
	OPTIONS:
	
	ModeType - aperture mode approximations, one of光场模式近似类型，选项包括：
	  'rectangle': rectangle function
	  'gaussian': spot size gaussian
	  'solve': 1D effective index method1D有效折射率法
	  'full': 2D rigorous FDFD simulation2D严格的FDFD仿真
	UseMagneticField - use magnetic field in overlap integrals在重叠积分中使用磁场
	TaperLosses - apply individual taper loss amount in +dB应用单独的锥形损耗（单位：dB）
	ExtraLosses - apply overall insertion loss bias in +dB应用总的插入损耗偏差（单位：dB）
	PhaseStdError - apply random phase error to each waveguide according to normally distributed noise function with provided standard error根据正态分布的噪声函数，为每个波导应用随机相位误差（标准误差）
	CustomInputFunction - provide arbitrary input field distribution instead of automatically generate field from waveguide description提供自定义输入场分布，而不是根据波导描述自动生成场分布
	"""

	__slots__ = [
				"ModeType",# 模式类型
				"UseMagneticField",# 是否使用磁场
				"InsertionLoss",# 插入损耗
				"PropagationLoss",# 传播损耗
				"PhaseErrorVariance",# 相位误差方差
				"CustomInputField"]# 自定义输入场

	def __init__(self,**kwargs):

		_in  = kwargs.keys()
		self.ModeType = kwargs["ModeType"] if "ModeType" in _in else "gaussian"# 设置模式类型，默认为'gaussian'（高斯模式）
		if self.ModeType.lower() not in ['rect','gaussian','solve']:# 检查模式类型是否合法
			raise ValueError("Mode type must be 'rect','gaussian'or 'solve'.")

		if "UseMagneticField" in _in:# 是否使用磁场，默认为False
			self.UseMagneticField = kwargs["UseMagneticField"]
		else:
			self.UseMagneticField = False

		if type(self.UseMagneticField) != bool:# 检查UseMagneticField的类型，必须为布尔值
			raise TypeError("UseMagneticField must be a boolean")

		self.InsertionLoss = kwargs["InsertionLoss"] if "InsertionLoss" in _in else 0# 设置插入损耗，默认为0
		if self.InsertionLoss < 0: # 插入损耗不能小于0
			raise ValueError("The insertion loss must be bigger or equal to 0")

		if "PropagationLoss" in _in:# 设置传播损耗，默认为0
			self.PropagationLoss = kwargs["PropagationLoss"]
		else:
			self.PropagationLoss = 0

		if self.PropagationLoss < 0:# 传播损耗不能小于0
			raise ValueError("The propagation loss must be bigger or equal to 0")

		if "PhaseErrorVariance" in _in:# 设置相位误差方差，默认为0
			self.PhaseErrorVariance = kwargs["PhaseErrorVariance"]
		else:
			self.PhaseErrorVariance = 0

		if self.PhaseErrorVariance < 0:# 相位误差方差不能小于0
			raise ValueError("The phase error variance must be bigger or equal to 0")

		if "CustomInputField" in _in: # 设置自定义输入场，默认为空列表
			self.CustomInputField = kwargs["CustomInputField"]
		else:
			self.CustomInputField = []
