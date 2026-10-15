/-
Formalia · 条目 #20261014-59
猜想：Conjectures about the Mandelbrot and Multibrot sets
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Mandelbrot.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Logic.Function.Defs
public import Mathlib.MeasureTheory.Measure.MeasureSpaceDef
public import Mathlib.Topology.Defs.Basic
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.Ring.Defs
public import Mathlib.Analysis.CStarAlgebra.Classes
public import Mathlib.Analysis.Normed.Ring.Basic
public import Mathlib.Data.Complex.Basic
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Set.CoeSort
public import Mathlib.Data.Set.Defs
public import Mathlib.Logic.Function.Iterate
public import Mathlib.Order.Filter.AtTopBot.Defs
public import Mathlib.Order.Filter.Defs
public import Mathlib.Topology.Bornology.Basic
public import Mathlib.Topology.Connected.LocallyConnected
public import Mathlib.Topology.Defs.Induced
public import Mathlib.Topology.MetricSpace.Pseudo.Defs
public import Mathlib.Topology.UniformSpace.Defs

@[expose] public section

namespace Registry.ConjecturesAboutTheMandelbrotAndMultibrotSets

namespace S20261014_59_aux

open Topology Set Function Filter Bornology Metric MeasureTheory

def multibrotSet (n : ℕ) : Set ℂ :=
  {c | ¬ Tendsto (fun k ↦ (fun z ↦ z ^ n + c)^[k] 0) atTop (cobounded ℂ)}

abbrev mandelbrotSet := multibrotSet 2

end S20261014_59_aux

open S20261014_59_aux in
/-- 表述 #20261014-59。

The MLC conjecture, stating that the mandelbrot set is locally connected. -/
def S20261014_59 : Prop :=
  LocallyConnectedSpace mandelbrotSet

end Registry.ConjecturesAboutTheMandelbrotAndMultibrotSets

end
