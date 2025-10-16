
########### food_pre4 - 12 ##########

******* problem file for debug *********
(:objects 
 	(agent1 - agent)
 	(Fork1 - object)
 	(Spoon1 - object)
 	(SoapBottle1 - object)
 	(Lettuce2 - object)
 	(Lettuce1 - object)
 	(Bowl1 - object)
 	(Plate1 - object)
 	(Lettuce3 - object)
 	(Fork2 - object)
 	(Apple1 - object)
 	(ButterKnife1 - object)
 	(CounterTop1 - receptacle)
 	(GarbageCan1 - receptacle)
 	(Plate2 - receptacle)
 	(Pot2 - receptacle)
 	(SinkBasin1 - receptacle)
 	(Plate1 - receptacle)
 	(SinkBasin3 - receptacle)
 	(Pot1 - receptacle)
 	(SinkBasin2 - receptacle)
 	(Mug1 - receptacle)
 	(GarbageCan2 - receptacle)
 	(Egg1 - object)
 	(DiningTable1 - receptacle)
 )
(:init 
 	(sliceable Lettuce2)
 	(sliceable Lettuce1)
 	(sliceable Apple1)
 	(sliceable Lettuce3)
 	(heatable Apple1)
 	(coolable Lettuce2)
 	(coolable Lettuce1)
 	(coolable Apple1)
 	(coolable Lettuce3)
 	(objectAtLocation Fork1 Plate1)
 	(objectAtLocation Spoon1 CounterTop1)
 	(objectAtLocation Bowl1 SinkBasin1)
 	(objectAtLocation ButterKnife1 Mug1)
 	(objectAtLocation Apple1 GarbageCan1)
 	(objectAtLocation SoapBottle1 GarbageCan2)
 	(objectAtLocation Lettuce1 Pot1)
 	(objectAtLocation Plate1 SinkBasin2)
 	(objectAtLocation Lettuce2 Plate2)
 	(objectAtLocation Fork2 Pot2)
 	(objectAtLocation Lettuce3 SinkBasin3)
 	(objectAtLocation Egg1 Pot2)
 )
Output:
(:goal (and
        (objectAtLocation Plate1 DiningTable1)
    )
)
****** Goal in Natural Language query ********
Write the goal specification in natural language.
Output:
(:goal (and
        (objectAtLocation Plate1 DiningTable1)
        (objectAtLocation Fork1 DiningTable1)
        (objectAtLocation Spoon1 DiningTable1)
        (objectAtLocation Bowl1 DiningTable1)
        (objectAtLocation ButterKnife1 DiningTable1)
        (objectAtLocation Apple1 DiningTable1)
        (objectAtLocation Lettuce1 DiningTable1)
        (objectAtLocation Lettuce2 DiningTable1)
        (objectAtLocation Lettuce3 DiningTable1)
        (objectAtLocation Egg1 DiningTable1)
    )
)
******* Domain understanding query ********
What does "prepare a meal" mean? What are the relevant objects for preparing a meal?
Output:
(:goal (and
        (objectAtLocation Plate1 DiningTable1)
       )
)