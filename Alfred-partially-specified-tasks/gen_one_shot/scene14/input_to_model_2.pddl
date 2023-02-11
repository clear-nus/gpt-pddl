PDDL: (define (domain put_task)
 (:requirements :typing :adl)
 (:types
    agent - dummy
    receptacle - dummy
    object -dummy
    receptacle_object - receptacle
    receptacle_object - object
  )

 (:predicates
    (atLocation ?a - agent ?l - receptacle)
    (objectAtLocation ?o - object ?l - receptacle)
    (inReceptacle ?o - object ?r - receptacle)
    (isReceptacleObject ?o - object)
    (holds ?a - agent ?o - object)
    (holdsAny ?a - agent)
    (holdsAnyReceptacleObject ?a - agent)
    (isClean ?o - object)
    (cleanable ?o - object)
    (isHot ?o - object)
    (heatable ?o - object)
    (isCool ?o - object)
    (coolable ?o - object)
    (toggleable ?o - object)
    (isOn ?o - object)
    (isToggled ?o - object)
    (sliceable ?o - object)
    (isSliced ?o - object)
    (isSinkBasin ?r - receptacle)
    (isMicrowave ?r - receptacle)
    (isFridge ?r - receptacle)
    (isKnife ?o - object)
    (isCounterTop ?o - object)
 )

 (:action GotoLocation
    :parameters (?a - agent ?lStart - receptacle ?lEnd - receptacle)
    :precondition (and
            (atLocation ?a ?lStart)
            )
    :effect (and
                (atLocation ?a ?lEnd)
                (not (atLocation ?a ?lStart))
            )
 )



 (:action PickupObjectInReceptacle
    :parameters (?a - agent ?o - object ?r - receptacle)
    :precondition (and
            (atLocation ?a ?r)
            (objectAtLocation ?o ?r)
            (inReceptacle ?o ?r)
            (not (holdsAny ?a))
            )
    :effect (and
                (not (inReceptacle ?o ?r))
                (not (objectAtLocation ?o ?r))
                (holds ?a ?o)
                (holdsAny ?a)
            )
 )

 (:action PickupObjectNoReceptacle
    :parameters (?a - agent ?o - object ?r - receptacle)
    :precondition (and
            (atLocation ?a ?r)
            (objectAtLocation ?o ?r)
            (not (inReceptacle ?o ?r))
            (not (holdsAny ?a))
            )
    :effect (and
                (not (objectAtLocation ?o ?r))
                (holds ?a ?o)
                (holdsAny ?a)
            )
 )

 (:action PutObjectInReceptacle
    :parameters (?a - agent ?o - object ?r - receptacle)
    :precondition (and
            (atLocation ?a ?r)
            (holds ?a ?o)
            (not (holdsAnyReceptacleObject ?a))
            )
    :effect (and
                (inReceptacle ?o ?r)
                (not (holds ?a ?o))
                (not (holdsAny ?a))
                (objectAtLocation ?o ?r)
            )
 )

 (:action PutObjectInReceptacleObject
    :parameters (?a - agent ?o - object ?outerO ?outerR - receptacle)
    :precondition (and
            (atLocation ?a ?outerR)
            (objectAtLocation ?outerO ?outerR)
            (isReceptacleObject ?outerO)
            (not (isReceptacleObject ?o))
            (holds ?a ?o)
            (not (holdsAnyReceptacleObject ?a))
            (inReceptacle ?outerO ?outerR)
            )
    :effect (and
                (inReceptacle ?o ?outerO)
                (inReceptacle ?o ?outerR)
                (not (holds ?a ?o))
                (not (holdsAny ?a))
                (objectAtLocation ?o ?outerR)
            )
 )

 (:action PutReceptacleObjectInReceptacle
    :parameters (?a - agent ?outerO - object ?r - receptacle)
    :precondition (and
            (atLocation ?a ?r)
            (holds ?a ?outerO)
            (holdsAnyReceptacleObject ?a)
            (isReceptacleObject ?outerO)
            )
    :effect (and
                (forall (?obj - object)
                    (when (holds ?a ?obj)
                        (and
                            (not (holds ?a ?obj))
                            (objectAtLocation ?obj ?r)
                            (inReceptacle ?obj ?r)
                        )
                    )
                )
                (not (holdsAny ?a))
                (not (holdsAnyReceptacleObject ?a))
            )
 )

 (:action CleanObject
    :parameters (?a - agent ?o - object ?l - receptacle)
    :precondition (and
            (isSinkBasin ?l)
            (atLocation ?a ?l)
            (holds ?a ?o)
            )
    :effect (and
                (isClean ?o)
            )
 )

 (:action HeatObject
    :parameters (?a - agent ?o - object ?l - receptacle)
    :precondition (and
            (or
                (isMicrowave ?l)
            )
            (atLocation ?a ?l)
            (holds ?a ?o)
            )
    :effect (and
                (isHot ?o)
            )
 )

 (:action CoolObject
    :parameters (?a - agent ?o - object ?l - receptacle)
    :precondition (and
            (or
                (isFridge ?l)
            )
            (atLocation ?a ?l)
            (holds ?a ?o)
            )
    :effect (and
                (isCool ?o)
            )
 )

 (:action ToggleObject
    :parameters (?a - agent ?o - object ?l - receptacle)
    :precondition (and
            (atLocation ?a ?l)
            (objectAtLocation ?o ?l)
            (toggleable ?o)
            )
    :effect (and
                (when (isOn ?o)
                    (not (isOn ?o)))
                (when (not (isOn ?o))
                    (isOn ?o))
                (isToggled ?o)
            )
 )

 (:action SliceObject
    :parameters (?a - agent ?co - object ?ko - object ?l - receptacle)
    :precondition
            (and
                (isKnife ?ko)
                (atLocation ?a ?l)
                (objectAtLocation ?co ?l)
                (sliceable ?co)
                (holds ?a ?ko)
                (isCounterTop ?l)
            )
    :effect (and
                (isSliced ?co)
            )
 )
)
Task: 
(:objects 
 	(CreditCard2 - object)
 	(KeyChain2 - object)
 	(Watch1 - object)
 	(Pencil1 - object)
 	(KeyChain1 - object)
 	(Pen1 - object)
 	(CellPhone1 - object)
 	(Book1 - object)
 	(Pillow1 - object)
 	(Book2 - object)
 	(Pencil2 - object)
 	(CreditCard1 - object)
 	(Box2 - receptacle_object)
 	(Box1 - receptacle_object)
 	(Desk2 - receptacle)
 	(Sofa1 - receptacle)
 	(Desk1 - receptacle)
 	(GarbageCan1 - receptacle)
 	(Drawer1 - receptacle)
 	(Sofa2 - receptacle)
 	(Bed1 - receptacle)
 	(Drawer4 - receptacle)
 	(Drawer2 - receptacle)
 	(Drawer3 - receptacle)
 	(AlarmClock1 - object)
 	(Box3 - receptacle_object)
 	(Box4 - receptacle_object)
 	(Sofa3 - receptacle)
 )
(:init 
 	(objectAtLocation Book1 Desk1)
 	(objectAtLocation CreditCard1 Desk2)
 	(objectAtLocation Pillow1 Sofa1)
 	(objectAtLocation Pencil1 GarbageCan1)
 	(objectAtLocation Watch1 Drawer1)
 	(objectAtLocation Pencil2 Drawer2)
 	(objectAtLocation Book2 Drawer3)
 	(objectAtLocation Pen1 Drawer4)
 	(objectAtLocation CellPhone1 Bed1)
 	(objectAtLocation KeyChain1 Sofa2)
 	(objectAtLocation AlarmClock1 Desk2)
 	(objectAtLocation KeyChain1 Box2)
 	(objectAtLocation Box2 Box3)
 	(objectAtLocation Box1 Sofa2)
 	(objectAtLocation Box3 Sofa1)
 	(objectAtLocation Box4 Sofa1)
 )
    
Put Pencil2 on the sofa with KeyChain1. Do not put it in box.
Answer: 
 
        (:goal (and
                (objectAtLocation Pencil2 Sofa1)
            )
        )            
Task: 
(:objects 
 	(agent1 - agent)
 	(Pillow1 - object)
 	(Pen2 - object)
 	(Pencil1 - object)
 	(Pen1 - object)
 	(CD1 - object)
 	(CreditCard1 - object)
 	(Book1 - object)
 	(AlarmClock2 - object)
 	(Book3 - object)
 	(Book2 - object)
 	(AlarmClock1 - object)
 	(Watch1 - object)
 	(Box1 - object)
 	(CellPhone1 - object)
 	(Laptop1 - object)
 	(Drawer2 - receptacle)
 	(Bed1 - receptacle)
 	(Desk2 - receptacle)
 	(Box4 - receptacle_object)
 	(Bed2 - receptacle)
 	(Desk1 - receptacle)
 	(Box3 - receptacle_object)
 	(GarbageCan2 - receptacle)
 	(Drawer1 - receptacle)
 	(Box2 - receptacle_object)
 	(Sofa1 - receptacle)
 	(Box1 - receptacle_object)
 	(Bed3 - receptacle)
 	(GarbageCan1 - receptacle)
 	(Desk3 - receptacle)
 	(Sofa2 - receptacle)
 	(Sofa3 - receptacle)
 )
(:init 
 	(objectAtLocation Book1 Sofa1)
 	(objectAtLocation Laptop1 Desk1)
 	(objectAtLocation CD1 GarbageCan1)
 	(objectAtLocation CreditCard1 Drawer1)
 	(objectAtLocation Pillow1 Bed1)
 	(objectAtLocation Pencil1 Drawer2)
 	(objectAtLocation Book2 Bed2)
 	(objectAtLocation AlarmClock2 Desk3)
 	(objectAtLocation Pen2 GarbageCan2)
 	(objectAtLocation CellPhone1 Bed3)
 	(objectAtLocation AlarmClock1 Box4)
 	(objectAtLocation Box4 Box2)
 	(objectAtLocation Box1 Sofa3)
 	(objectAtLocation Box2 Sofa1)
 	(objectAtLocation Box3 Sofa1)
 )
Put the Book1 on the sofa with AlarmClock1. Do not put it in box.
Write the instruction to goal state in PDDL. 
Answer: