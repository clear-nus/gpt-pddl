(define (domain put_task)
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