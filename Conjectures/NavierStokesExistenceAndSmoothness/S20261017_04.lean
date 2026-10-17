/-
Formalia · 条目 #20261017-04
猜想：Navier–Stokes existence and smoothness
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2026 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Millenium/NavierStokes.lean（提交 8bf45ed）。
改动：去掉属性与 `sorry`，局部记号改写为完整名称，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。辅助定义与原文逐项一致。
-/
module

public import Mathlib.Analysis.InnerProductSpace.PiL2
public import Mathlib.Analysis.Calculus.FDeriv.Basic
public import Mathlib.LinearAlgebra.Trace
public import Mathlib.Analysis.Calculus.ContDiff.Defs
public import Mathlib.Analysis.Calculus.ContDiff.FTaylorSeries
public import Mathlib.Analysis.Calculus.Deriv.Basic
public import Mathlib.Analysis.InnerProductSpace.Laplacian
public import Mathlib.Analysis.Calculus.Gradient.Basic
public import Mathlib.MeasureTheory.Function.LpSeminorm.Defs
public import Mathlib.MeasureTheory.Integral.Bochner.Basic
public import Mathlib.MeasureTheory.Measure.Haar.InnerProductSpace

@[expose] public section

namespace Registry.NavierStokesExistenceAndSmoothness

namespace S20261017_04_aux

/-- 向量场 `v : ℝⁿ → ℝⁿ` 在点 `x` 处的散度，定义为雅可比矩阵的迹，即 `∑ᵢ ∂vᵢ/∂xᵢ`。
`v` 在 `x` 处不可微时，`fderiv` 取零映射，散度相应地取 0。 -/
noncomputable def divergence {n : ℕ} (v : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    (x : EuclideanSpace ℝ (Fin n)) : ℝ :=
  (fderiv ℝ v x).trace ℝ (EuclideanSpace ℝ (Fin n))

/-- 函数在每个坐标方向上以 1 为周期：对每个单位向量 `eᵢ` 有 `f (x + eᵢ) = f x`。
这刻画了 n 维环面 `ℝⁿ/ℤⁿ` 上的函数。 -/
def IsOnePeriodic {n : ℕ} {α : Sort*} (f : EuclideanSpace ℝ (Fin n) → α) : Prop :=
  ∀ x i, f (x + EuclideanSpace.single i 1) = f x

/-- 初始速度场的基本条件：无散（不可压缩）且光滑（`C^∞`）。 -/
structure InitialVelocityCondition {n : ℕ}
    (u₀ : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n)) : Prop where
  /-- 初始速度场无散（方程 2）。 -/
  div_free : ∀ x, divergence u₀ x = 0
  /-- 初始速度场光滑。 -/
  smooth : ContDiff ℝ ((⊤ : ℕ∞) : WithTop ℕ∞) u₀

/-- 全空间 `ℝⁿ` 上的初始速度条件：除光滑、无散外，各阶导数在无穷远处比任何多项式衰减得都快（条件 4）。 -/
structure InitialVelocityConditionDecay {n : ℕ}
    (u₀ : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n)) : Prop
    extends InitialVelocityCondition u₀ where
  /-- 对任意导数阶 `m` 和衰减速率 `K`，存在 `C` 使 `‖∂ᵐu₀(x)‖ ≤ C/(1+‖x‖)^K`。 -/
  decay : ∀ m : ℕ, ∀ K : ℝ, ∃ C : ℝ, ∀ x, ‖iteratedFDeriv ℝ m u₀ x‖ ≤ C / (1 + ‖x‖) ^ K

/-- 周期情形 `ℝⁿ/ℤⁿ` 的初始速度条件：光滑、无散，且在每个坐标方向上以 1 为周期（条件 8 前半）。 -/
structure InitialVelocityConditionPeriodic {n : ℕ}
    (u₀ : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n)) : Prop
    extends InitialVelocityCondition u₀ where
  /-- 初始速度在每个方向上以 1 为周期。 -/
  isOnePeriodic : IsOnePeriodic u₀

/-- 外力的基本光滑性条件：`f(x,t)` 在 `ℝⁿ × [0,∞)` 上光滑。 -/
structure ForceCondition {n : ℕ}
    (f : EuclideanSpace ℝ (Fin n) → ℝ → EuclideanSpace ℝ (Fin n)) : Prop where
  /-- 外力在 `ℝⁿ × [0,∞)` 上光滑。 -/
  smooth : ContDiffOn ℝ ((⊤ : ℕ∞) : WithTop ℕ∞) (↿f) (Set.univ ×ˢ Set.Ici 0)

/-- 全空间 `ℝⁿ` 上的外力条件：光滑，且各阶导数在空间和时间上比任何多项式衰减得都快（条件 5）。 -/
structure ForceConditionDecay {n : ℕ}
    (f : EuclideanSpace ℝ (Fin n) → ℝ → EuclideanSpace ℝ (Fin n)) : Prop
    extends ForceCondition f where
  /-- 对 `t ≥ 0`，`‖∂ᵐ_{x,t} f(x,t)‖ ≤ C/(1+‖x‖+t)^K`。 -/
  decay : ∀ m : ℕ, ∀ K : ℝ, ∃ C : ℝ, ∀ x, ∀ t ≥ 0,
    ‖iteratedFDerivWithin ℝ m (↿f) (Set.univ ×ˢ Set.Ici 0) (x, t)‖ ≤ C / (1 + ‖x‖ + t) ^ K

/-- 周期情形 `ℝⁿ/ℤⁿ` 的外力条件：光滑、在空间上以 1 为周期，且在时间上快速衰减（条件 8 前半、条件 9）。 -/
structure ForceConditionPeriodic {n : ℕ}
    (f : EuclideanSpace ℝ (Fin n) → ℝ → EuclideanSpace ℝ (Fin n)) : Prop
    extends ForceCondition f where
  /-- 对所有 `t ≥ 0`，外力在空间上以 1 为周期。 -/
  isOnePeriodic : ∀ t ≥ 0, IsOnePeriodic (f · t)
  /-- 各阶导数在时间上比任何多项式衰减得都快。 -/
  decay : ∀ m : ℕ, ∀ K : ℝ, ∃ C : ℝ, ∀ x, ∀ t ≥ 0,
    ‖iteratedFDerivWithin ℝ m (↿f) (Set.univ ×ˢ Set.Ici 0) (x, t)‖ ≤ C / (1 + t) ^ K

/-- 粘性系数 `nu`、初始速度 `u₀`、外力 `f` 下纳维-斯托克斯方程的解 `(v, p)`：
满足方程（1）、对所有时间无散（2）、满足初始条件（3），且在 `t ≥ 0` 上光滑（6、11）。 -/
structure NavierStokesExistenceAndSmoothness {n : ℕ}
    (nu : ℝ) (u₀ : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    (f : EuclideanSpace ℝ (Fin n) → ℝ → EuclideanSpace ℝ (Fin n))
    (v : EuclideanSpace ℝ (Fin n) → ℝ → EuclideanSpace ℝ (Fin n))
    (p : EuclideanSpace ℝ (Fin n) → ℝ → ℝ) : Prop where
  /-- 方程（1）：`∂v/∂t + (v·∇)v = νΔv − ∇p + f`。时间导数取在 `[0,∞)` 内。 -/
  navier_stokes : ∀ x, ∀ t ≥ 0,
    derivWithin (v x ·) (Set.Ici 0) t + fderiv ℝ (v · t) x (v x t) =
      nu • Laplacian.laplacian (v · t) x - gradient (p · t) x + f x t
  /-- 不可压缩条件（2）：对所有 `x` 和 `t ≥ 0`，`∇·v = 0`。 -/
  div_free : ∀ x, ∀ t ≥ 0, divergence (v · t) x = 0
  /-- 初始条件（3）：`v(x,0) = u₀(x)`。 -/
  initial_condition : ∀ x, v x 0 = u₀ x
  /-- 速度在 `ℝⁿ × [0,∞)` 上光滑。 -/
  velocity_smooth : ContDiffOn ℝ ((⊤ : ℕ∞) : WithTop ℕ∞) (↿v) (Set.univ ×ˢ Set.Ici 0)
  /-- 压力在 `ℝⁿ × [0,∞)` 上光滑。 -/
  pressure_smooth : ContDiffOn ℝ ((⊤ : ℕ∞) : WithTop ℕ∞) (↿p) (Set.univ ×ˢ Set.Ici 0)

/-- 全空间 `ℝⁿ` 上的解：在上面的基础上，每个时刻速度平方可积，且总能量对所有时间一致有界（条件 7）。 -/
structure NavierStokesExistenceAndSmoothnessRn {n : ℕ}
    (nu : ℝ) (u₀ : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    (f : EuclideanSpace ℝ (Fin n) → ℝ → EuclideanSpace ℝ (Fin n))
    (v : EuclideanSpace ℝ (Fin n) → ℝ → EuclideanSpace ℝ (Fin n))
    (p : EuclideanSpace ℝ (Fin n) → ℝ → ℝ) : Prop
    extends NavierStokesExistenceAndSmoothness nu u₀ f v p where
  /-- 每个时刻 `t ≥ 0` 速度平方可积。 -/
  integrable : ∀ t ≥ 0, MeasureTheory.MemLp (‖v · t‖) 2
  /-- 动能 `∫ ‖v(x,t)‖² dx` 对所有时间一致有界。 -/
  globally_bounded_energy : ∃ E, ∀ t ≥ 0, (∫ x : EuclideanSpace ℝ (Fin n), ‖v x t‖ ^ 2) < E

/-- 环面 `ℝⁿ/ℤⁿ` 上的解：速度在所有时刻都以 1 为周期（条件 10）；
按克雷问题说明附录的勘误，压力也要求以 1 为周期。 -/
structure NavierStokesExistenceAndSmoothnessPeriodic {n : ℕ}
    (nu : ℝ) (u₀ : EuclideanSpace ℝ (Fin n) → EuclideanSpace ℝ (Fin n))
    (f : EuclideanSpace ℝ (Fin n) → ℝ → EuclideanSpace ℝ (Fin n))
    (v : EuclideanSpace ℝ (Fin n) → ℝ → EuclideanSpace ℝ (Fin n))
    (p : EuclideanSpace ℝ (Fin n) → ℝ → ℝ) : Prop
    extends NavierStokesExistenceAndSmoothness nu u₀ f v p where
  /-- 速度在所有 `t ≥ 0` 时以 1 为周期。 -/
  isOnePeriodic_velocity : ∀ t ≥ 0, IsOnePeriodic (v · t)
  /-- 压力在所有 `t ≥ 0` 时以 1 为周期（克雷勘误）。 -/
  isOnePeriodic_pressure : ∀ t ≥ 0, IsOnePeriodic (p · t)

end S20261017_04_aux

open S20261017_04_aux in
/-- 表述 #20261017-04。

(D) Breakdown of (forced) Navier–Stokes solutions on ℝ³/ℤ³. -/
def S20261017_04 : Prop :=
  ∀ (nu : ℝ), nu > 0 → ∃ (u₀ : EuclideanSpace ℝ (Fin 3) → EuclideanSpace ℝ (Fin 3)) (f : EuclideanSpace ℝ (Fin 3) → ℝ → EuclideanSpace ℝ (Fin 3)),
    InitialVelocityConditionPeriodic u₀ ∧ ForceConditionPeriodic f ∧
    ¬ (∃ v p, NavierStokesExistenceAndSmoothnessPeriodic nu u₀ f v p)

end Registry.NavierStokesExistenceAndSmoothness

end
