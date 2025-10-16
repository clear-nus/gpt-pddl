
########### food_pre2 - 11 ##########

******* problem file for debug *********
(:objects 
 	(agent1 - agent)
 	(Fork1 - object)
 	(Knife1 - object)
 	(Bread1 - object)
 	(Tomato1 - object)
 	(ButterKnife3 - object)
 	(Bowl1 - object)
 	(Ladle1 - object)
 	(ButterKnife2 - object)
 	(Potato1 - object)
 	(Egg1 - object)
 	(ButterKnife1 - object)
 	(Pan2 - receptacle)
 	(Cabinet1 - receptacle)
 	(GarbageCan1 - receptacle)
 	(Bowl1 - receptacle)
 	(Bowl2 - receptacle)
 	(Plate1 - receptacle)
 	(Pot1 - receptacle)
 	(Pot2 - receptacle)
 	(Mug1 - receptacle)
 	(Pan1 - receptacle)
 	(GarbageCan2 - receptacle)
 	(Apple1 - object)
 )
(:init 
 	(sliceable Egg1)
 	(sliceable Bread1)
 	(sliceable Tomato1)
 	(sliceable Potato1)
 	(heatable Egg1)
 	(heatable Bread1)
 	(heatable Tomato1)
 	(heatable Potato1)
 	(coolable Egg1)
 	(coolable Bread1)
 	(coolable Tomato1)
 	(coolable Potato1)
 	(objectAtLocation Fork1 Pan1)
 	(objectAtLocation Potato1 Plate1)
 	(objectAtLocation ButterKnife1 Bowl1)
 	(objectAtLocation Egg1 Bowl2)
 	(objectAtLocation Tomato1 GarbageCan1)
 	(objectAtLocation ButterKnife2 Mug1)
 	(objectAtLocation Knife1 Pot1)
 	(objectAtLocation Bread1 GarbageCan2)
 	(objectAtLocation Ladle1 Pan2)
 	(objectAtLocation Bowl1 Cabinet1)
 	(objectAtLocation ButterKnife3 Pot2)
 	(objectAtLocation Apple1 Cabinet1)
 )
Output:
Based on the description provided, the task of cutting fruits and placing them on a plate translates into the following PDDL goal state. The slicing action implies that the fruits should be in a sliced state, and placing them on a plate means the fruits should end up in the plate receptacle after being sliced.

Given the objects Tomato1 and Apple1 as fruits in the initial state, the goal would look like this:

```lisp
(:goal (and
        (isSliced Tomato1)
        (isSliced Apple1)
        (inReceptacle Tomato1 Plate1)
        (inReceptacle Apple1 Plate1)
       )
)
```

This goal state specifies that both Tomato1 and Apple1 must be sliced (`isSliced`) and they must be in the Plate1 (`inReceptacle` with Tomato1 and Apple1 `Plate1` as parameters).