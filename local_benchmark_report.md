# Local MathRAG Benchmark Report

**Date:** Fri Feb 13 12:11:16 2026
**Strategy:** Custom `StructureAwareChunker` + Hybrid Retrieval (BGE-Large + BM25)
**Average Hybrid Score:** 0.0157 (Note: Hybrid scores are RRF-weighted, not direct cosine)

## Detailed Results

| Query | Score | Latency (s) | Preview |
| :--- | :---: | :---: | :--- |
| What are the questions in Exercise 3.1? | **0.0115** | 7.68 | 48 MATHEMATICS Solution  Here l = 37.4 cm and θ = 60° = 60π π radian = 180 3 Hence, by r = θ l , we have r = 37.4×3 37.4×3×7 = π 22  = 35.7 cm Example... |
| Find the radian measures: (i) 25 degrees (ii) -47 degrees 30 minutes | **0.0163** | 0.59 | 48 MATHEMATICS Solution  Here l = 37.4 cm and θ = 60° = 60π π radian = 180 3 Hence, by r = θ l , we have r = 37.4×3 37.4×3×7 = π 22  = 35.7 cm Example... |
| How many rotations does a wheel make if it turns 360 times in one minute? | **0.0163** | 0.47 | 44 MATHEMATICS called the initial side and the final position of the ray after rotation is called the terminal side of the angle. The point of rotatio... |
| Show Example 13 | **0.0164** | 0.68 | TRIGONOMETRIC FUNCTIONS     65 Solution We have tan 13 12 π = tan  12 π   π +     = tan  tan 12 4 6 π π π   = −     = tan tan 4 6 1 tan ta... |
| Prove that (sin x + sin 3x) / (cos x + cos 3x) = tan 2x | **0.0163** | 0.58 | TRIGONOMETRIC FUNCTIONS     71 Hence tan  x 2  =  sin cos x x 2 2 3 10 10 1 = × −       = – 3. Example 22    Prove that cos2 x + cos2 2 π π 3 co... |
| What is the relation between radian and real numbers? | **0.0164** | 0.50 | 46 MATHEMATICS 3.2.3  Relation between radian and real numbers Consider the unit circle with centre O. Let A be any point on the circle. Consider OA a... |
| Find the degree measure of 11/16 radians | **0.0163** | 0.44 | 46 MATHEMATICS 3.2.3  Relation between radian and real numbers Consider the unit circle with centre O. Let A be any point on the circle. Consider OA a... |
| A pendulum swings through an angle of radian if its length is 75 cm | **0.0164** | 0.46 | 48 MATHEMATICS Solution  Here l = 37.4 cm and θ = 60° = 60π π radian = 180 3 Hence, by r = θ l , we have r = 37.4×3 37.4×3×7 = π 22  = 35.7 cm Example... |


## Full Retrieval Content (Top 1)
### 1. What are the questions in Exercise 3.1?
- **Score:** 0.0115
- **Latency:** 7.6807s
- **Retrieved Chunk:**
```text
48
MATHEMATICS
Solution  Here l = 37.4 cm and θ = 60° = 60π
π
radian =
180
3
Hence,
by r = θ
l , we have
r = 37.4×3
37.4×3×7
=
π
22
 = 35.7 cm
Example 4   The minute hand of a watch is 1.5 cm long. How far does its tip move in
40 minutes? (Use π = 3.14).
Solution  In 60 minutes, the minute hand of a watch completes one revolution. Therefore,
in 40 minutes, the minute hand turns through 2
3  of a revolution. Therefore,  
2
θ =
× 360°
3
or 4π
3  radian. Hence, the required distance travelled is given by
 l = r θ  =  1.5 × 4π
3
cm = 2π cm = 2 ×3.14 cm = 6.28 cm.
Example 5  If the arcs of the same lengths in two circles subtend angles 65°and 110°
at the centre, find the ratio of their radii.
Solution  Let r1 and r2 be the radii of the two circles. Given that
θ1 = 65° = π
65
180 ×
 = 13π
36  radian
and
θ2  = 110° = π
110
180 ×
 = 22π
36 radian
Let l be the length of each of the arc. Then l =  r1θ1 =  r2θ2, which gives
13π
36  ×r1 = 22π
36  × r2 ,  i.e., 
1
2
r
r = 22
13
Hence
 r1 : r2 = 22 : 13.
EXERCISE 3.1
1.
Find the radian measures corresponding to the following degree measures:
(i) 25°
(ii) – 47°30′
(iii) 240°
     (iv) 520°
Reprint 2025-26


TRIGONOMETRIC FUNCTIONS     49
2.
Find the degree measures corresponding to the following radian measures
(Use 
22
π
7
=
).
(i)
11
16
(ii)
– 4
(iii)
5π
3
(iv)
7π
6
3.
A wheel makes 360 revolutions in one minute. Through how many radians does
it turn in one second?
4.
Find the degree measure of the angle subtended at the centre of a circle of
radius 100 cm by an arc of length 22 cm (Use 
22
π
7
=
).
5.
In a circle of diameter 40 cm, the length of a chord is 20 cm. Find the length of
minor arc of the chord.
6.
If in two circles, arcs of the same length subtend angles 60° and 75°  at the
centre, find the ratio of their radii.
7.
Find the angle in radian through which a pendulum swings if its length is 75 cm
and th e tip describes an arc of length
(i)
10 cm
(ii)
15 cm
(iii)
21 cm
3.3  Trigonometric Functions
In earlier classes, we have studied trigonometric ratios for acute angles as the ratio of
sides of a right angled triangle. We will now extend the definition of trigonometric
ratios to any angle in terms of radian measure and study them as trigonometric functions.
Consider a unit circle with centre
at origin of the coordinate axes. Let
P (a, b) be any point on the circle with
angle AOP = x radian, i.e., length of arc
AP = x (Fig 3.6).
We define cos x = a and sin x =  b
Since ∆OMP is a right triangle, we have
OM2 + MP2 = OP2 or a2 + b2 = 1
Thus, for every point on the unit circle,
we have
a2 + b2 = 1 or cos2 x + sin2 x = 1
Since one complete revolution
subtends an angle of 2π radian at the
centre of the circle,  ∠AOB = π
2 ,
Fig  3.6
Reprint 2025-26


50
MATHEMATICS
∠AOC = π and  ∠AOD = 3π
2 . All angles which are integral multiples of π
2  are called
quadrantal angles. The coordinates of the points A, B, C and D are, respectively,
(1, 0), (0, 1), (–1, 0) and (0, –1). Therefore, for quadrantal angles, we have
cos 0° = 1
sin 0° = 0,
cos π
2 = 0
sin π
2 = 1
cosπ = − 1
sinπ = 0
cos 3π
2
= 0
sin 3π
2
= –1
cos 2π = 1
sin 2π = 0
Now, if we take one complete revolution from the point P, we again come back to
same point P. Thus, we also observe that if x increases (or decreases) by any integral
multiple of 2π, the values of sine and cosine functions do not change. Thus,
sin (2nπ + x)  = sinx, n ∈ Z ,  cos (2nπ + x) = cosx, n ∈ Z
Further, sin x = 0, if x = 0, ± π,  ± 2π , ± 3π, ..., i.e., when x is an integral multiple of π
and cos x = 0, if x = ± π
2 , ± 3π
2  , ± 5π
2 , ... i.e., cos x vanishes when x is an odd
multiple of π
2 . Thus
sin x  = 0 implies x = nπ, 
π, 
π, 
π, 
π, where n is any integer
cos x = 0 implies x = (2n + 1) π
2 , where n is any integer.
We now define other trigonometric functions in terms of sine and cosine functions:
cosec x = 
1
sin x , x ≠  nπ, where n is any integer.
sec x    = 
1
cosx , x ≠ (2n + 1) π
2 , where n is any  integer.
tan x     = sin
cos
x
x , x ≠ (2n +1) π
2 , where n is any integer.
cot x     = cos
sin
x
x , x ≠ n π, where n is any integer.
Reprint 2025-26


TRIGONOMETRIC FUNCTIONS     51
not
defined
not
defined
We have shown that for all real x,  sin2 x + cos2 x = 1
It follows that
1 + tan2 x = sec2 x
(why?)
1 + cot2 x = cosec2 x
(why?)
In earlier classes, we have discussed the values of trigonometric ratios for 0°,
30°, 45°, 60° and 90°. The values of trigonometric functions for these angles are same
as that of trigonometric ratios studied in earlier classes. Thus, we have the following
table:
0°
π
6
π
4
π
3
π
2
π
3π
2
2π
sin
0
1
2
1
2
3
2
1
 0
– 1
 0
cos
1
3
2
1
2
 1
2
0
– 1
  0
 1
tan
0
1
3
  1
3
  0
 0
The values of cosec x, sec x and cot x
are the reciprocal of the values of sin x,
cos x and tan x, respectively.
3.3.1  Sign of trigonometric functions
Let P (a, b) be a point on the unit circle
with centre at the origin such that
∠AOP = x. If ∠AOQ = – x, then the
coordinates of the point Q will be (a, –b)
(Fig 3.7). Therefore
cos (– x) = cos x
and
sin (– x) = – sin x
Since for every point P (a, b) on
the unit circle, – 1 ≤ a ≤ 1 and
Fig  3.7
Reprint 2025-26


52
MATHEMATICS
– 1 ≤  b ≤ 1, we have – 1 ≤ cos x ≤ 1 and –1 ≤ sin x ≤ 1 for all x. We   have learnt in
previous classes that in the first quadrant (0 < x < π
2 ) a and b are both positive, in the
second quadrant ( π
2  < x <π) a is negative and b is positive, in the third quadrant
(π < x < 3π
2 ) a and b are both negative and in the fourth quadrant ( 3π
2  < x < 2π) a is
positive and b is negative. Therefore, sin x is positive for 0 < x < π, and negative for
π < x < 2π. Similarly, cos x is positive for 0 < x < π
2 , negative for π
2  <  x < 3π
2  and also
positive for 3π
2 <  x < 2π. Likewise, we can find the signs of other trigonometric
functions in different quadrants. In fact, we have the following table.
I
II
III
IV
sin x
+
+
 –
 –
cos x
+
 –
 –
 +
tan x
+
 –
 +
 –
cosec x
+
+
 –
 –
sec x
+
 –
 –
 +
cot x
+
 –
 +
 –
3.3.2  Domain and range of trigonometric functions  From the definition of sine
and cosine functions, we observe that they are defined for all real numbers. Further,
we observe that for each real number x,
 – 1 ≤ sin x ≤ 1 and  – 1 ≤ cos x ≤ 1
Thus, domain of y = sin x and y = cos x is the set of all real numbers and range
is the interval [–1, 1], i.e., – 1 ≤ y ≤ 1.
Reprint 2025-26


TRIGONOMETRIC FUNCTIONS     53
Since cosec x = 
1
sin x , the domain of y = cosec x is the set { x : x ∈ R and
x ≠ n π, n ∈ Z} and range is the set {y : y ∈ R, y  ≥ 1 or y  ≤ – 1}. Similarly, the domain
of y = sec x is the set {x : x ∈ R and x ≠ (2n + 1) π
2 , n ∈ Z} and range is the set
{y : y  ∈ R, y  ≤ – 1or y ≥ 1}. The domain of y = tan x is the set {x : x ∈ R and
x ≠ (2n + 1) π
2 , n ∈ Z} and range is the set of all real numbers. The domain of
y = cot x is the set {x : x  ∈ R and x ≠ n π, n ∈ Z} and the range is the set of all real
numbers.
We further observe that in the first quadrant, as x increases from 0 to π
2 , sin x
increases from 0 to 1, as x increases from π
2  to π, sin x decreases from 1 to 0. In the
third quadrant, as x increases from π to 3π
2 , sin x decreases from 0 to –1and finally, in
the fourth quadrant, sin x increases from –1 to 0 as x increases from 3π
2  to 2π.
Similarly, we can discuss the behaviour of other trigonometric functions. In fact, we
have the following table:
Remark In the above table, the statement tan x increases from 0 to ∞ (infinity) for
0 < x < π
2  simply means that tan x increases as x increases for 0 < x < π
2  and
I quadrant
II quadrant
III quadrant
IV quadrant
sin
increases from 0 to 1
decreases from 1 to 0
decreases from 0 to –1 increases from –1 to 0
cos
decreases from 1 to 0
decreases from 0 to – 1 increases from –1 to 0
increases from 0 to 1
tan
increases from 0 to ∞increases from –∞to 0
increases from 0 to ∞
increases from –∞to 0
cot
decreases from ∞ to 0 decreases from 0 to–∞decreases from ∞ to 0
decreases from 0to –∞
sec
increases from 1 to ∞increases from –∞to–1 decreases from –1to–∞decreases from ∞ to 1
cosec decreases from ∞ to 1 increases from 1 to ∞
increases from –∞to–1 decreases from–1to–∞
Reprint 2025-26


54
MATHEMATICS
Fig 3.10
Fig 3.11
Fig 3.8
Fig 3.9
assumes arbitraily large positive values as x approaches to π
2 .  Similarly, to say that
cosec x decreases from –1 to – ∞ (minus infinity) in the fourth quadrant means that
cosec x decreases for x ∈ ( 3π
2 , 2π) and assumes arbitrarily large negative values as
x approaches to 2π. The symbols ∞ and  – ∞ simply specify certain types of behaviour
of functions and variables.
We have already seen that values of sin x and cos x repeats after an interval of
2π. Hence, values of cosec x and sec x will also repeat after an interval of 2π. We
Reprint 2025-26

```
---
### 2. Find the radian measures: (i) 25 degrees (ii) -47 degrees 30 minutes
- **Score:** 0.0163
- **Latency:** 0.5905s
- **Retrieved Chunk:**
```text
48
MATHEMATICS
Solution  Here l = 37.4 cm and θ = 60° = 60π
π
radian =
180
3
Hence,
by r = θ
l , we have
r = 37.4×3
37.4×3×7
=
π
22
 = 35.7 cm
Example 4   The minute hand of a watch is 1.5 cm long. How far does its tip move in
40 minutes? (Use π = 3.14).
Solution  In 60 minutes, the minute hand of a watch completes one revolution. Therefore,
in 40 minutes, the minute hand turns through 2
3  of a revolution. Therefore,  
2
θ =
× 360°
3
or 4π
3  radian. Hence, the required distance travelled is given by
 l = r θ  =  1.5 × 4π
3
cm = 2π cm = 2 ×3.14 cm = 6.28 cm.
Example 5  If the arcs of the same lengths in two circles subtend angles 65°and 110°
at the centre, find the ratio of their radii.
Solution  Let r1 and r2 be the radii of the two circles. Given that
θ1 = 65° = π
65
180 ×
 = 13π
36  radian
and
θ2  = 110° = π
110
180 ×
 = 22π
36 radian
Let l be the length of each of the arc. Then l =  r1θ1 =  r2θ2, which gives
13π
36  ×r1 = 22π
36  × r2 ,  i.e., 
1
2
r
r = 22
13
Hence
 r1 : r2 = 22 : 13.
EXERCISE 3.1
1.
Find the radian measures corresponding to the following degree measures:
(i) 25°
(ii) – 47°30′
(iii) 240°
     (iv) 520°
Reprint 2025-26


TRIGONOMETRIC FUNCTIONS     49
2.
Find the degree measures corresponding to the following radian measures
(Use 
22
π
7
=
).
(i)
11
16
(ii)
– 4
(iii)
5π
3
(iv)
7π
6
3.
A wheel makes 360 revolutions in one minute. Through how many radians does
it turn in one second?
4.
Find the degree measure of the angle subtended at the centre of a circle of
radius 100 cm by an arc of length 22 cm (Use 
22
π
7
=
).
5.
In a circle of diameter 40 cm, the length of a chord is 20 cm. Find the length of
minor arc of the chord.
6.
If in two circles, arcs of the same length subtend angles 60° and 75°  at the
centre, find the ratio of their radii.
7.
Find the angle in radian through which a pendulum swings if its length is 75 cm
and th e tip describes an arc of length
(i)
10 cm
(ii)
15 cm
(iii)
21 cm
3.3  Trigonometric Functions
In earlier classes, we have studied trigonometric ratios for acute angles as the ratio of
sides of a right angled triangle. We will now extend the definition of trigonometric
ratios to any angle in terms of radian measure and study them as trigonometric functions.
Consider a unit circle with centre
at origin of the coordinate axes. Let
P (a, b) be any point on the circle with
angle AOP = x radian, i.e., length of arc
AP = x (Fig 3.6).
We define cos x = a and sin x =  b
Since ∆OMP is a right triangle, we have
OM2 + MP2 = OP2 or a2 + b2 = 1
Thus, for every point on the unit circle,
we have
a2 + b2 = 1 or cos2 x + sin2 x = 1
Since one complete revolution
subtends an angle of 2π radian at the
centre of the circle,  ∠AOB = π
2 ,
Fig  3.6
Reprint 2025-26


50
MATHEMATICS
∠AOC = π and  ∠AOD = 3π
2 . All angles which are integral multiples of π
2  are called
quadrantal angles. The coordinates of the points A, B, C and D are, respectively,
(1, 0), (0, 1), (–1, 0) and (0, –1). Therefore, for quadrantal angles, we have
cos 0° = 1
sin 0° = 0,
cos π
2 = 0
sin π
2 = 1
cosπ = − 1
sinπ = 0
cos 3π
2
= 0
sin 3π
2
= –1
cos 2π = 1
sin 2π = 0
Now, if we take one complete revolution from the point P, we again come back to
same point P. Thus, we also observe that if x increases (or decreases) by any integral
multiple of 2π, the values of sine and cosine functions do not change. Thus,
sin (2nπ + x)  = sinx, n ∈ Z ,  cos (2nπ + x) = cosx, n ∈ Z
Further, sin x = 0, if x = 0, ± π,  ± 2π , ± 3π, ..., i.e., when x is an integral multiple of π
and cos x = 0, if x = ± π
2 , ± 3π
2  , ± 5π
2 , ... i.e., cos x vanishes when x is an odd
multiple of π
2 . Thus
sin x  = 0 implies x = nπ, 
π, 
π, 
π, 
π, where n is any integer
cos x = 0 implies x = (2n + 1) π
2 , where n is any integer.
We now define other trigonometric functions in terms of sine and cosine functions:
cosec x = 
1
sin x , x ≠  nπ, where n is any integer.
sec x    = 
1
cosx , x ≠ (2n + 1) π
2 , where n is any  integer.
tan x     = sin
cos
x
x , x ≠ (2n +1) π
2 , where n is any integer.
cot x     = cos
sin
x
x , x ≠ n π, where n is any integer.
Reprint 2025-26


TRIGONOMETRIC FUNCTIONS     51
not
defined
not
defined
We have shown that for all real x,  sin2 x + cos2 x = 1
It follows that
1 + tan2 x = sec2 x
(why?)
1 + cot2 x = cosec2 x
(why?)
In earlier classes, we have discussed the values of trigonometric ratios for 0°,
30°, 45°, 60° and 90°. The values of trigonometric functions for these angles are same
as that of trigonometric ratios studied in earlier classes. Thus, we have the following
table:
0°
π
6
π
4
π
3
π
2
π
3π
2
2π
sin
0
1
2
1
2
3
2
1
 0
– 1
 0
cos
1
3
2
1
2
 1
2
0
– 1
  0
 1
tan
0
1
3
  1
3
  0
 0
The values of cosec x, sec x and cot x
are the reciprocal of the values of sin x,
cos x and tan x, respectively.
3.3.1  Sign of trigonometric functions
Let P (a, b) be a point on the unit circle
with centre at the origin such that
∠AOP = x. If ∠AOQ = – x, then the
coordinates of the point Q will be (a, –b)
(Fig 3.7). Therefore
cos (– x) = cos x
and
sin (– x) = – sin x
Since for every point P (a, b) on
the unit circle, – 1 ≤ a ≤ 1 and
Fig  3.7
Reprint 2025-26


52
MATHEMATICS
– 1 ≤  b ≤ 1, we have – 1 ≤ cos x ≤ 1 and –1 ≤ sin x ≤ 1 for all x. We   have learnt in
previous classes that in the first quadrant (0 < x < π
2 ) a and b are both positive, in the
second quadrant ( π
2  < x <π) a is negative and b is positive, in the third quadrant
(π < x < 3π
2 ) a and b are both negative and in the fourth quadrant ( 3π
2  < x < 2π) a is
positive and b is negative. Therefore, sin x is positive for 0 < x < π, and negative for
π < x < 2π. Similarly, cos x is positive for 0 < x < π
2 , negative for π
2  <  x < 3π
2  and also
positive for 3π
2 <  x < 2π. Likewise, we can find the signs of other trigonometric
functions in different quadrants. In fact, we have the following table.
I
II
III
IV
sin x
+
+
 –
 –
cos x
+
 –
 –
 +
tan x
+
 –
 +
 –
cosec x
+
+
 –
 –
sec x
+
 –
 –
 +
cot x
+
 –
 +
 –
3.3.2  Domain and range of trigonometric functions  From the definition of sine
and cosine functions, we observe that they are defined for all real numbers. Further,
we observe that for each real number x,
 – 1 ≤ sin x ≤ 1 and  – 1 ≤ cos x ≤ 1
Thus, domain of y = sin x and y = cos x is the set of all real numbers and range
is the interval [–1, 1], i.e., – 1 ≤ y ≤ 1.
Reprint 2025-26


TRIGONOMETRIC FUNCTIONS     53
Since cosec x = 
1
sin x , the domain of y = cosec x is the set { x : x ∈ R and
x ≠ n π, n ∈ Z} and range is the set {y : y ∈ R, y  ≥ 1 or y  ≤ – 1}. Similarly, the domain
of y = sec x is the set {x : x ∈ R and x ≠ (2n + 1) π
2 , n ∈ Z} and range is the set
{y : y  ∈ R, y  ≤ – 1or y ≥ 1}. The domain of y = tan x is the set {x : x ∈ R and
x ≠ (2n + 1) π
2 , n ∈ Z} and range is the set of all real numbers. The domain of
y = cot x is the set {x : x  ∈ R and x ≠ n π, n ∈ Z} and the range is the set of all real
numbers.
We further observe that in the first quadrant, as x increases from 0 to π
2 , sin x
increases from 0 to 1, as x increases from π
2  to π, sin x decreases from 1 to 0. In the
third quadrant, as x increases from π to 3π
2 , sin x decreases from 0 to –1and finally, in
the fourth quadrant, sin x increases from –1 to 0 as x increases from 3π
2  to 2π.
Similarly, we can discuss the behaviour of other trigonometric functions. In fact, we
have the following table:
Remark In the above table, the statement tan x increases from 0 to ∞ (infinity) for
0 < x < π
2  simply means that tan x increases as x increases for 0 < x < π
2  and
I quadrant
II quadrant
III quadrant
IV quadrant
sin
increases from 0 to 1
decreases from 1 to 0
decreases from 0 to –1 increases from –1 to 0
cos
decreases from 1 to 0
decreases from 0 to – 1 increases from –1 to 0
increases from 0 to 1
tan
increases from 0 to ∞increases from –∞to 0
increases from 0 to ∞
increases from –∞to 0
cot
decreases from ∞ to 0 decreases from 0 to–∞decreases from ∞ to 0
decreases from 0to –∞
sec
increases from 1 to ∞increases from –∞to–1 decreases from –1to–∞decreases from ∞ to 1
cosec decreases from ∞ to 1 increases from 1 to ∞
increases from –∞to–1 decreases from–1to–∞
Reprint 2025-26


54
MATHEMATICS
Fig 3.10
Fig 3.11
Fig 3.8
Fig 3.9
assumes arbitraily large positive values as x approaches to π
2 .  Similarly, to say that
cosec x decreases from –1 to – ∞ (minus infinity) in the fourth quadrant means that
cosec x decreases for x ∈ ( 3π
2 , 2π) and assumes arbitrarily large negative values as
x approaches to 2π. The symbols ∞ and  – ∞ simply specify certain types of behaviour
of functions and variables.
We have already seen that values of sin x and cos x repeats after an interval of
2π. Hence, values of cosec x and sec x will also repeat after an interval of 2π. We
Reprint 2025-26

```
---
### 3. How many rotations does a wheel make if it turns 360 times in one minute?
- **Score:** 0.0163
- **Latency:** 0.4740s
- **Retrieved Chunk:**
```text
44
MATHEMATICS
called the initial side and the final position of the ray after rotation is called the
terminal side of the angle. The point of rotation is called the vertex. If the direction of
rotation is anticlockwise, the angle is said to be positive and if the direction of rotation
is clockwise, then the angle is negative (Fig 3.1).
The measure of an angle is the amount of
rotation performed to get the terminal side from
the initial side. There are several units for
measuring angles. The definition of an angle
suggests a unit, viz. one complete revolution from the position of the initial side as
indicated in Fig 3.2.
This is often convenient for large angles. For example, we can say that a rapidly
spinning wheel is making an angle of say 15 revolution per second. We shall  describe
two other units of measurement of an angle which are most commonly used, viz.
degree measure and radian measure.
3.2.1  Degree measure  If a rotation from the initial side to terminal side is 
th
1
360





of
a revolution, the angle is said to have a measure of one degree, written as 1°.  A degree is
divided into 60 minutes, and a minute is divided into 60 seconds . One sixtieth of a degree is
called a minute, written as 1′, and one sixtieth of a minute is called a second, written as 1″.
Thus,
1° = 60′,
1′ = 60″
Some of the angles whose measures are 360°,180°, 270°, 420°, – 30°, – 420° are
shown in Fig 3.3.
Fig  3.2
Fig  3.3
Reprint 2025-26

```
---
### 4. Show Example 13
- **Score:** 0.0164
- **Latency:** 0.6775s
- **Retrieved Chunk:**
```text
TRIGONOMETRIC FUNCTIONS     65
Solution We have
tan 13
12
π = tan 
12
π


π +



 = tan 
tan
12
4
6
π
π
π


=
−




=
tan
tan
4
6
1
tan
tan
4
6
π
π
−
π
π
+
= 
1
1
3
1
3
2
3
1
3
1
1
3
−
−
=
=
−
+
+
Example 13 Prove that
sin(
)
tan
tan
sin(
)
tan
tan
x
y
x
y
x
y
x
y
+
+
=
−
−
.
Solution We have
              L.H.S.
sin(
)
sin cos
cos sin
sin(
)
sin cos
cos sin
x
y
x
y
x
y
x
y
x
y
x
y
+
+
=
=
−
−
Dividing the numerator and denominator by cos x cos y, we get
sin(
)
tan
tan
sin(
)
tan
tan
x
y
x
y
x
y
x
y
+
+
=
−
−
.
Example 14  Show that
   tan 3 x tan 2 x tan x = tan 3x – tan 2 x – tan x
Solution We know that 3x = 2x + x
Therefore,
tan 3x = tan (2x + x)
or
tan2
tan
tan3
1– tan 2 tan
x
x
x
x
x
+
=
or
tan 3x – tan 3x tan 2x tan x = tan 2x + tan x
or
tan 3x – tan 2x – tan x = tan 3x tan 2x tan x
or
tan 3x tan 2x tan x = tan 3x – tan 2x – tan x.
Example 15 Prove that
cos
cos
2 cos
4
4
x
x
x
π
π




+
+
−
=








Solution Using the Identity 20(i), we have
Reprint 2025-26

```
---
### 5. Prove that (sin x + sin 3x) / (cos x + cos 3x) = tan 2x
- **Score:** 0.0163
- **Latency:** 0.5807s
- **Retrieved Chunk:**
```text
TRIGONOMETRIC FUNCTIONS     71
Hence
tan 
x
2  = 
sin
cos
x
x
2
2
3
10
10
1
=
× −





 = – 3.
Example 22    Prove that cos2 x + cos2
2
π
π
3
cos
3
3
2
x
x




+
+
−
=








.
Solution    We have
      L.H.S. = 
2π
2π
1
cos 2
1
cos 2
1
cos 2
3
3
2
2
2
x
x
x




+
+
+
−




+




+
+
.
= 
1
2π
2π
3
cos 2
cos 2
cos 2
2
3
3
x
x
x






+
+
+
+
−












= 
1
2π
3
cos 2
2cos 2
cos
2
3
x
x


+
+




= 
1
π
3
cos 2
2cos 2 cos π
2
3
x
x




+
+
−








= 
1
π
3
cos 2
2cos 2 cos
2
3
x
x


+
−




= 
[
]
1
3
3
cos 2
cos 2
2
2
x
x
+
−
=
 = R.H.S.
Miscellaneous Exercise on Chapter 3
Prove that:
1.
0
13
π
5
cos
13
π
3
cos
13
π
9
cos
13
π
cos
2
=
+
+
2.
(sin 3x + sin x) sin x + (cos 3x – cos x) cos x = 0
3.
(cos x + cos y)2 + (sin x – sin y)2 = 4 cos2  
2
x
y
+
Reprint 2025-26

```
---
### 6. What is the relation between radian and real numbers?
- **Score:** 0.0164
- **Latency:** 0.4968s
- **Retrieved Chunk:**
```text
46
MATHEMATICS
3.2.3  Relation between radian and real numbers
Consider the unit circle with centre O. Let A be any point
on the circle. Consider OA as initial side of an angle.
Then the length  of an arc of the circle will give the radian
measure of the angle which the arc will subtend at the
centre of the circle. Consider the line PAQ which is
tangent to the circle at A. Let the point A represent the
real number zero, AP represents positive real number and
AQ represents negative real numbers (Fig 3.5). If we
rope the line AP in the anticlockwise direction along the
circle, and AQ in the clockwise direction, then every real
number will correspond to a radian measure and
conversely. Thus, radian measures and real numbers can
be considered as one and the same.
3.2.4   Relation between degree and radian   Since a circle subtends at the centre
an angle whose radian measure is 2π and its degree measure is 360°, it follows that
2π radian = 360°
  or
π radian = 180°
The above relation enables us to express a radian measure in terms of degree
measure and a degree measure in terms of radian measure. Using approximate value
of π as 22
7 , we have
1 radian = 180
π
° = 57° 16′ approximately.
Also
1° = π
180  radian  =  0.01746 radian approximately.
The relation between degree measures and radian measure of some common angles
are given in the following table:
A
O
1
P
1
2
−1
−2
Q
0
Fig  3.5
Degree
30°
45°
60°
90°
180°
270°
360°
Radian
π
6
π
4
π
3
π
2
π
3π
2
2π
Reprint 2025-26

```
---
### 7. Find the degree measure of 11/16 radians
- **Score:** 0.0163
- **Latency:** 0.4418s
- **Retrieved Chunk:**
```text
46
MATHEMATICS
3.2.3  Relation between radian and real numbers
Consider the unit circle with centre O. Let A be any point
on the circle. Consider OA as initial side of an angle.
Then the length  of an arc of the circle will give the radian
measure of the angle which the arc will subtend at the
centre of the circle. Consider the line PAQ which is
tangent to the circle at A. Let the point A represent the
real number zero, AP represents positive real number and
AQ represents negative real numbers (Fig 3.5). If we
rope the line AP in the anticlockwise direction along the
circle, and AQ in the clockwise direction, then every real
number will correspond to a radian measure and
conversely. Thus, radian measures and real numbers can
be considered as one and the same.
3.2.4   Relation between degree and radian   Since a circle subtends at the centre
an angle whose radian measure is 2π and its degree measure is 360°, it follows that
2π radian = 360°
  or
π radian = 180°
The above relation enables us to express a radian measure in terms of degree
measure and a degree measure in terms of radian measure. Using approximate value
of π as 22
7 , we have
1 radian = 180
π
° = 57° 16′ approximately.
Also
1° = π
180  radian  =  0.01746 radian approximately.
The relation between degree measures and radian measure of some common angles
are given in the following table:
A
O
1
P
1
2
−1
−2
Q
0
Fig  3.5
Degree
30°
45°
60°
90°
180°
270°
360°
Radian
π
6
π
4
π
3
π
2
π
3π
2
2π
Reprint 2025-26

```
---
### 8. A pendulum swings through an angle of radian if its length is 75 cm
- **Score:** 0.0164
- **Latency:** 0.4599s
- **Retrieved Chunk:**
```text
48
MATHEMATICS
Solution  Here l = 37.4 cm and θ = 60° = 60π
π
radian =
180
3
Hence,
by r = θ
l , we have
r = 37.4×3
37.4×3×7
=
π
22
 = 35.7 cm
Example 4   The minute hand of a watch is 1.5 cm long. How far does its tip move in
40 minutes? (Use π = 3.14).
Solution  In 60 minutes, the minute hand of a watch completes one revolution. Therefore,
in 40 minutes, the minute hand turns through 2
3  of a revolution. Therefore,  
2
θ =
× 360°
3
or 4π
3  radian. Hence, the required distance travelled is given by
 l = r θ  =  1.5 × 4π
3
cm = 2π cm = 2 ×3.14 cm = 6.28 cm.
Example 5  If the arcs of the same lengths in two circles subtend angles 65°and 110°
at the centre, find the ratio of their radii.
Solution  Let r1 and r2 be the radii of the two circles. Given that
θ1 = 65° = π
65
180 ×
 = 13π
36  radian
and
θ2  = 110° = π
110
180 ×
 = 22π
36 radian
Let l be the length of each of the arc. Then l =  r1θ1 =  r2θ2, which gives
13π
36  ×r1 = 22π
36  × r2 ,  i.e., 
1
2
r
r = 22
13
Hence
 r1 : r2 = 22 : 13.
EXERCISE 3.1
1.
Find the radian measures corresponding to the following degree measures:
(i) 25°
(ii) – 47°30′
(iii) 240°
     (iv) 520°
Reprint 2025-26


TRIGONOMETRIC FUNCTIONS     49
2.
Find the degree measures corresponding to the following radian measures
(Use 
22
π
7
=
).
(i)
11
16
(ii)
– 4
(iii)
5π
3
(iv)
7π
6
3.
A wheel makes 360 revolutions in one minute. Through how many radians does
it turn in one second?
4.
Find the degree measure of the angle subtended at the centre of a circle of
radius 100 cm by an arc of length 22 cm (Use 
22
π
7
=
).
5.
In a circle of diameter 40 cm, the length of a chord is 20 cm. Find the length of
minor arc of the chord.
6.
If in two circles, arcs of the same length subtend angles 60° and 75°  at the
centre, find the ratio of their radii.
7.
Find the angle in radian through which a pendulum swings if its length is 75 cm
and th e tip describes an arc of length
(i)
10 cm
(ii)
15 cm
(iii)
21 cm
3.3  Trigonometric Functions
In earlier classes, we have studied trigonometric ratios for acute angles as the ratio of
sides of a right angled triangle. We will now extend the definition of trigonometric
ratios to any angle in terms of radian measure and study them as trigonometric functions.
Consider a unit circle with centre
at origin of the coordinate axes. Let
P (a, b) be any point on the circle with
angle AOP = x radian, i.e., length of arc
AP = x (Fig 3.6).
We define cos x = a and sin x =  b
Since ∆OMP is a right triangle, we have
OM2 + MP2 = OP2 or a2 + b2 = 1
Thus, for every point on the unit circle,
we have
a2 + b2 = 1 or cos2 x + sin2 x = 1
Since one complete revolution
subtends an angle of 2π radian at the
centre of the circle,  ∠AOB = π
2 ,
Fig  3.6
Reprint 2025-26


50
MATHEMATICS
∠AOC = π and  ∠AOD = 3π
2 . All angles which are integral multiples of π
2  are called
quadrantal angles. The coordinates of the points A, B, C and D are, respectively,
(1, 0), (0, 1), (–1, 0) and (0, –1). Therefore, for quadrantal angles, we have
cos 0° = 1
sin 0° = 0,
cos π
2 = 0
sin π
2 = 1
cosπ = − 1
sinπ = 0
cos 3π
2
= 0
sin 3π
2
= –1
cos 2π = 1
sin 2π = 0
Now, if we take one complete revolution from the point P, we again come back to
same point P. Thus, we also observe that if x increases (or decreases) by any integral
multiple of 2π, the values of sine and cosine functions do not change. Thus,
sin (2nπ + x)  = sinx, n ∈ Z ,  cos (2nπ + x) = cosx, n ∈ Z
Further, sin x = 0, if x = 0, ± π,  ± 2π , ± 3π, ..., i.e., when x is an integral multiple of π
and cos x = 0, if x = ± π
2 , ± 3π
2  , ± 5π
2 , ... i.e., cos x vanishes when x is an odd
multiple of π
2 . Thus
sin x  = 0 implies x = nπ, 
π, 
π, 
π, 
π, where n is any integer
cos x = 0 implies x = (2n + 1) π
2 , where n is any integer.
We now define other trigonometric functions in terms of sine and cosine functions:
cosec x = 
1
sin x , x ≠  nπ, where n is any integer.
sec x    = 
1
cosx , x ≠ (2n + 1) π
2 , where n is any  integer.
tan x     = sin
cos
x
x , x ≠ (2n +1) π
2 , where n is any integer.
cot x     = cos
sin
x
x , x ≠ n π, where n is any integer.
Reprint 2025-26


TRIGONOMETRIC FUNCTIONS     51
not
defined
not
defined
We have shown that for all real x,  sin2 x + cos2 x = 1
It follows that
1 + tan2 x = sec2 x
(why?)
1 + cot2 x = cosec2 x
(why?)
In earlier classes, we have discussed the values of trigonometric ratios for 0°,
30°, 45°, 60° and 90°. The values of trigonometric functions for these angles are same
as that of trigonometric ratios studied in earlier classes. Thus, we have the following
table:
0°
π
6
π
4
π
3
π
2
π
3π
2
2π
sin
0
1
2
1
2
3
2
1
 0
– 1
 0
cos
1
3
2
1
2
 1
2
0
– 1
  0
 1
tan
0
1
3
  1
3
  0
 0
The values of cosec x, sec x and cot x
are the reciprocal of the values of sin x,
cos x and tan x, respectively.
3.3.1  Sign of trigonometric functions
Let P (a, b) be a point on the unit circle
with centre at the origin such that
∠AOP = x. If ∠AOQ = – x, then the
coordinates of the point Q will be (a, –b)
(Fig 3.7). Therefore
cos (– x) = cos x
and
sin (– x) = – sin x
Since for every point P (a, b) on
the unit circle, – 1 ≤ a ≤ 1 and
Fig  3.7
Reprint 2025-26


52
MATHEMATICS
– 1 ≤  b ≤ 1, we have – 1 ≤ cos x ≤ 1 and –1 ≤ sin x ≤ 1 for all x. We   have learnt in
previous classes that in the first quadrant (0 < x < π
2 ) a and b are both positive, in the
second quadrant ( π
2  < x <π) a is negative and b is positive, in the third quadrant
(π < x < 3π
2 ) a and b are both negative and in the fourth quadrant ( 3π
2  < x < 2π) a is
positive and b is negative. Therefore, sin x is positive for 0 < x < π, and negative for
π < x < 2π. Similarly, cos x is positive for 0 < x < π
2 , negative for π
2  <  x < 3π
2  and also
positive for 3π
2 <  x < 2π. Likewise, we can find the signs of other trigonometric
functions in different quadrants. In fact, we have the following table.
I
II
III
IV
sin x
+
+
 –
 –
cos x
+
 –
 –
 +
tan x
+
 –
 +
 –
cosec x
+
+
 –
 –
sec x
+
 –
 –
 +
cot x
+
 –
 +
 –
3.3.2  Domain and range of trigonometric functions  From the definition of sine
and cosine functions, we observe that they are defined for all real numbers. Further,
we observe that for each real number x,
 – 1 ≤ sin x ≤ 1 and  – 1 ≤ cos x ≤ 1
Thus, domain of y = sin x and y = cos x is the set of all real numbers and range
is the interval [–1, 1], i.e., – 1 ≤ y ≤ 1.
Reprint 2025-26


TRIGONOMETRIC FUNCTIONS     53
Since cosec x = 
1
sin x , the domain of y = cosec x is the set { x : x ∈ R and
x ≠ n π, n ∈ Z} and range is the set {y : y ∈ R, y  ≥ 1 or y  ≤ – 1}. Similarly, the domain
of y = sec x is the set {x : x ∈ R and x ≠ (2n + 1) π
2 , n ∈ Z} and range is the set
{y : y  ∈ R, y  ≤ – 1or y ≥ 1}. The domain of y = tan x is the set {x : x ∈ R and
x ≠ (2n + 1) π
2 , n ∈ Z} and range is the set of all real numbers. The domain of
y = cot x is the set {x : x  ∈ R and x ≠ n π, n ∈ Z} and the range is the set of all real
numbers.
We further observe that in the first quadrant, as x increases from 0 to π
2 , sin x
increases from 0 to 1, as x increases from π
2  to π, sin x decreases from 1 to 0. In the
third quadrant, as x increases from π to 3π
2 , sin x decreases from 0 to –1and finally, in
the fourth quadrant, sin x increases from –1 to 0 as x increases from 3π
2  to 2π.
Similarly, we can discuss the behaviour of other trigonometric functions. In fact, we
have the following table:
Remark In the above table, the statement tan x increases from 0 to ∞ (infinity) for
0 < x < π
2  simply means that tan x increases as x increases for 0 < x < π
2  and
I quadrant
II quadrant
III quadrant
IV quadrant
sin
increases from 0 to 1
decreases from 1 to 0
decreases from 0 to –1 increases from –1 to 0
cos
decreases from 1 to 0
decreases from 0 to – 1 increases from –1 to 0
increases from 0 to 1
tan
increases from 0 to ∞increases from –∞to 0
increases from 0 to ∞
increases from –∞to 0
cot
decreases from ∞ to 0 decreases from 0 to–∞decreases from ∞ to 0
decreases from 0to –∞
sec
increases from 1 to ∞increases from –∞to–1 decreases from –1to–∞decreases from ∞ to 1
cosec decreases from ∞ to 1 increases from 1 to ∞
increases from –∞to–1 decreases from–1to–∞
Reprint 2025-26


54
MATHEMATICS
Fig 3.10
Fig 3.11
Fig 3.8
Fig 3.9
assumes arbitraily large positive values as x approaches to π
2 .  Similarly, to say that
cosec x decreases from –1 to – ∞ (minus infinity) in the fourth quadrant means that
cosec x decreases for x ∈ ( 3π
2 , 2π) and assumes arbitrarily large negative values as
x approaches to 2π. The symbols ∞ and  – ∞ simply specify certain types of behaviour
of functions and variables.
We have already seen that values of sin x and cos x repeats after an interval of
2π. Hence, values of cosec x and sec x will also repeat after an interval of 2π. We
Reprint 2025-26

```
---
