# Alfred Open Ended Tasks (Alfred Task number 9 to 13)

## Tasks

The repository includes five household tasks:

- **food_pre2**: CutFruits - Slice fruits and place them on a plate
- **food_pre4**: PrepareMeal - Prepare and arrange meal components on the dining table
- **scene2**: IceCream - Put ice cream in the fridge where it belongs
- **scene4**: SetTable2 - Set the dining table for two people
- **scene6**: CleanKitchen - Clean up kitchen by organizing items

## File Structure

Each task folder contains:
- `init_state_*.pddl` - Initial state files (input)
- `goal_state_*.pddl` - Generated goal states (output)

The `domain/` folder contains the PDDL domain definition with actions like `PickupObject`, `PutObjectInReceptacle`, `SliceObject`, etc.

## Generation

The `openai_gen.py` script translates natural language instructions into PDDL goal specifications. It processes domain files, initial states, and natural language commands to generate structured goal states.

## Usage

```python
python openai_gen.py
```

Note: Set your OpenAI API key in the script before running.