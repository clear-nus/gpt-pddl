
########### food_pre4 - 20 ##########

******* problem file for debug *********
(:objects 
 	(agent1 - agent)
 	(Fork1 - object)
 	(SoapBottle1 - object)
 	(DishSponge1 - object)
 	(Spoon1 - object)
 	(Knife1 - object)
 	(Mug2 - object)
 	(Lettuce1 - object)
 	(Tomato1 - object)
 	(Knife2 - object)
 	(Spoon2 - object)
 	(Bowl1 - object)
 	(Mug1 - object)
 	(CounterTop1 - receptacle)
 	(Fridge1 - receptacle)
 	(GarbageCan1 - receptacle)
 	(Pot2 - receptacle)
 	(CounterTop2 - receptacle)
 	(SinkBasin1 - receptacle)
 	(Bowl1 - receptacle)
 	(Plate1 - receptacle)
 	(Pot1 - receptacle)
 	(Plate2 - receptacle)
 	(Plate3 - receptacle)
 	(Pan1 - receptacle)
 	(Egg1 - object)
 	(DiningTable1 - receptacle)
 )
(:init 
 	(sliceable Lettuce1)
 	(sliceable Tomato1)
 	(heatable Tomato1)
 	(coolable Lettuce1)
 	(coolable Tomato1)
 	(objectAtLocation SoapBottle1 GarbageCan1)
 	(objectAtLocation DishSponge1 Pan1)
 	(objectAtLocation Fork1 Bowl1)
 	(objectAtLocation Knife1 Plate1)
 	(objectAtLocation Spoon1 CounterTop1)
 	(objectAtLocation Bowl1 Fridge1)
 	(objectAtLocation Spoon2 SinkBasin1)
 	(objectAtLocation Tomato1 Plate2)
 	(objectAtLocation Mug1 Plate3)
 	(objectAtLocation Knife2 Pot1)
 	(objectAtLocation Mug2 CounterTop2)
 	(objectAtLocation Lettuce1 Pot2)
 	(objectAtLocation Egg1 SinkBasin1)
 )
Output:
(:goal (and
        (inReceptacle Tomato1 DiningTable1)
        (inReceptacle Lettuce1 DiningTable1)
    )
)
****** Goal in Natural Language query ********
Write the goal specification in natural language.
Output:
(:goal (and
        (objectAtLocation Tomato1 DiningTable1)
        (objectAtLocation Lettuce1 DiningTable1)
        (objectAtLocation Egg1 DiningTable1)
    )
)
******* Domain understanding query ********
What does "prepare a meal" mean? What are the relevant objects for preparing a meal?
Output:
(:goal (and
        (objectAtLocation Lettuce1 DiningTable1)
        (objectAtLocation Tomato1 DiningTable1)
        (objectAtLocation Egg1 DiningTable1)
        (isSliced Lettuce1)
        (isSliced Tomato1)
        (isHot Egg1)
    )
)