
########### food_pre2 - 16 ##########

******* problem file for debug *********
(:objects 
 	(agent1 - agent)
 	(DishSponge2 - object)
 	(Fork1 - object)
 	(Pan2 - object)
 	(DishSponge1 - object)
 	(Knife1 - object)
 	(Lettuce1 - object)
 	(Tomato1 - object)
 	(Knife2 - object)
 	(Apple1 - object)
 	(Plate1 - object)
 	(Ladle1 - object)
 	(Cup1 - object)
 	(Pan1 - object)
 	(ButterKnife1 - object)
 	(CounterTop1 - receptacle)
 	(Fridge1 - receptacle)
 	(Cabinet1 - receptacle)
 	(Mug1 - receptacle)
 	(Fridge2 - receptacle)
 	(Cabinet2 - receptacle)
 	(SinkBasin1 - receptacle)
 	(Bowl1 - receptacle)
 	(Bowl2 - receptacle)
 	(Pot1 - receptacle)
 	(SinkBasin2 - receptacle)
 	(Pot2 - receptacle)
 	(Pan1 - receptacle)
 	(Bowl3 - receptacle)
 	(Plate1 - receptacle)
 )
(:init 
 	(sliceable Lettuce1)
 	(sliceable Tomato1)
 	(sliceable Apple1)
 	(heatable Cup1)
 	(heatable Tomato1)
 	(heatable Apple1)
 	(coolable Lettuce1)
 	(coolable Tomato1)
 	(coolable Apple1)
 	(objectAtLocation Ladle1 Pan1)
 	(objectAtLocation DishSponge1 CounterTop1)
 	(objectAtLocation Pan1 SinkBasin1)
 	(objectAtLocation Plate1 Cabinet1)
 	(objectAtLocation Tomato1 Bowl1)
 	(objectAtLocation Knife1 Pot1)
 	(objectAtLocation Lettuce1 Bowl2)
 	(objectAtLocation DishSponge2 SinkBasin2)
 	(objectAtLocation ButterKnife1 Pot2)
 	(objectAtLocation Fork1 Bowl3)
 	(objectAtLocation Pan2 Fridge1)
 	(objectAtLocation Apple1 Fridge2)
 	(objectAtLocation Knife2 Mug1)
 	(objectAtLocation Cup1 Cabinet2)
 )
Output:
Based on the given PDDL domain, actions, and types, to achieve the goal of cutting some fruits and putting them on the plate, we can specify the goal state as follows:

```
(:goal (and
        (isSliced Apple1)
        (inReceptacle Apple1 Plate1)
       )
)
```

This goal state implies that the apple (as an example of a fruit based on the provided objects) is to be sliced (`isSliced Apple1`) and then placed on the plate (`inReceptacle Apple1 Plate1`).