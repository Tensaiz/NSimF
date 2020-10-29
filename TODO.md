# TODO

## General
- [ ] Add validation to all class members and throw meaningful warnings
- [ ] Add enums where applicable

## Model
- [x] Create scheme class
- [x] Add custom metric function support
- [x] Element wise neighbours / adjencency matrix
- [x] Write states optionally to disk + config
- [x] Implement state memory
- [x] Create built-in conditions
- [ ] Implement more memory
  - [ ] Utility memory
  - [ ] Adjacency memory
  - [ ] Graph memory
- [ ] Add non-array support
- [ ] Multi process update functions per iteration

## Dynamic network utility layer
### Utility
- [x] Utility per edge
- [x] Utility change
  - [x] NxN matrix
  - [ ] Specific edges
<!-- - [ ] Cost function definition -->
- [x] Optional utility initialization 
- [x] Threshold state conditions
- [ ] Amount of neighbors condition

### Network updating
- [x] Remove nodes
  - [x] List format
- [ ] Add nodes
  - [ ] Number specification
  - [ ] Optional state init
  - [ ] Optional utility init
  - [ ] Optional edges 
- [x] Edge change
  - [x] New adjacency matrix

## UI
- [ ] Add graphical UI for state / constant selection / distribution specification

## Update
- [x] Add support for conditions
- [ ] Set all chained condition state indices

## Examples
- [x] Add example runner
- [ ] Add example param specification

## Sensitivity Analysis
- [x] Add sensitivity analysis runner
- [x] Add SA metrics
  - [x] Means
  - [x] Variance
  - [x] Min / Max
  - [x] Network metrics
  - [x] Custom function
- [ ] Add parallel processing

## Visualization
- [x] Add more layout and networkx layout support
- [x] Read states from disk
- [ ] Smart reconfiguration visualization
- [ ] Add regular plots / trends
- [ ] Optimize animation if possible
- [ ] Support jupyter notebook

## Testing
- [ ] Write more tests

## Documentation
- [x] Implement ReadTheDocs
- [ ] Document code

## DevOps
- [x] Add CI support
- [x] Add code quality checking
- [x] Add automatic coverage checking
- [ ] Create contribution and pull request templates

## Package
- [x] Publish to PyPi
- [x] Add license