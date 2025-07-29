# Experimental Data Management System for Experimental Solutions

## Project Overview
This project is a system for experimental data management, providing a complete solution for front-end table interaction and back-end data processing. The system supports dynamic table creation, editing, data import/export, and other functions, suitable for scenarios such as laboratory solution formulation, concentration calculation, and experimental configuration management.

**Note:** The project is still under development. Currently, it can only calculate the concentration of new solutions based on raw material concentrations and addition amounts. 

Features to be completed:
- Batch formulation planning based on target concentrations (for multiple substances) and existing solutions (backend has preliminary implementation but lacks front-end support)
- Substance module
- Front-end support for JSON data handling

## Core Features
- Dynamically create and edit interactive tables
- Support adding and deleting table rows/columns
- Data pasting functionality, supporting data import from clipboard
- JSON serialization and deserialization of table data
- Saving and loading of experimental data
- Support for floating window table display
- Front-end and back-end interaction for experimental configuration
- Calculate new solution concentrations based on raw material concentrations and addition amounts

## Technology Stack
- Front-end: JavaScript (ES6+)
- Back-end: Python + Flask
- Data format: JSON

## Main Modules

### Experiment Class (Experiment.py)
The core class managing experimental data, including sample management, concentration calculations, and solution formulation.

#### Key Methods

##### `update_all_concentrations()`
Updates concentrations for all trials using topological sorting to handle dependencies:
```python
# Example of dependency graph construction and topological sorting
adj = defaultdict(list)
in_degree = defaultdict(int)
for trial in trials:
    for comp_name in trial.composite:
        # Build dependency relationships
        adj[comp_trial].append(trial)
        in_degree[trial] += 1

# Topological sort to handle calculation order
queue = deque([t for t in trials if in_degree.get(t, 0) == 0])
```

##### `_calculate_trial_concentration(trial: trial)`
Core concentration calculation logic:
```python
# Calculate total volume from components
total_vol = sum(trial.composite.values())

# Calculate substance amounts from components
substance_amounts = defaultdict(float)
for comp_name, vol_used in trial.composite.items():
    comp_trial = self.sample_dict.get(comp_name)[1]
    for sub, conc in comp_trial.substance_conc.items():
        substance_amounts[sub] += conc * vol_used

# Calculate final concentrations
trial.substance_conc = {
    sub: amount / total_vol
    for sub, amount in substance_amounts.items()
}
```

##### `design_concentration_advanced()`
Advanced concentration design algorithm (preliminary backend implementation):
```python
def design_concentration_advanced(
        self,
        target_conc: Dict[str, float],
        total_volume: float,
        min_volume: float = 1.0,
        max_volume: float = 100.0,
        max_retries: int = 3
) -> Tuple[str, Dict[str, float]]:
    # Generates substance-trial mapping
    # Implements recursive volume allocation
    # Handles solvent volume calculation
    # Creates final trial with target concentrations
```

##### `_handle_solvent()`
Handles solvent volume calculation and allocation:
```python
current_total = sum(volumes.values())
solvent_vol = total_volume - current_total
# Automatically finds or creates solvent entry
```

### Trial Class (trial.py)
Represents individual solution samples, including stocks and mixtures.

#### Key Methods

##### `create_stock()`
Static method to create stock solutions:
```python
@staticmethod
def create_stock(stock_name="", substance_conc=None, total_amount = -1, 
                 exp_name = "", solvent = False, id = "", s_info=None):
    the_stock = trial(name = stock_name, substance_conc=substance_conc, 
                     exp_name = exp_name, id = id, info=s_info,
                     total_amount = total_amount, existing_amount=total_amount, 
                     solvent= solvent, stock = True)
    return the_stock
```

## Usage Methods

### Creating Stock Solutions
1. Use `trial.create_stock()` to create stock solution instances
2. Add stocks to an experiment using `Experiment.generate_trial()`
3. Batch create stocks from 2D arrays with `stock_from_2d_array()`

### Calculating Concentrations
1. Define composite solutions with their component volumes
2. Call `update_all_concentrations()` to automatically calculate concentrations
3. The system handles dependency ordering using topological sorting

### Advanced Concentration Design
1. Define target concentrations for substances
2. Specify total volume and volume constraints
3. Call `design_concentration_advanced()` to get optimal mixture proportions

## Data Persistence
1. Save experiment data using `save_to_txt(filename)`
2. Load experiment data using `Experiment.load_from_txt(filename)`

## Notes
- The system uses topological sorting to handle concentration calculation order for composite solutions
- Circular dependencies in solution compositions will throw errors
- Volume calculations automatically handle solvent allocation
- Stock solutions and solvents have special handling in concentration calculations
- The batch formulation planning feature is currently under development (backend only)
