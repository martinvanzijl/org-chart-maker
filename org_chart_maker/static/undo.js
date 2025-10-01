// =============================================================================
// Undo framework.
// =============================================================================

// Undo block class.
class UndoBlock {
  // Constructor.
  constructor() {
    this.childUndos = [];
  }

  // Add an item.
  add(item) {
    this.childUndos.push(item);
  }

  // Check if empty.
  isEmpty() {
    return this.childUndos.length == 0;
  }

  // Redo.
  redo() {
    for (var index in self.childUndos) {
      self.childUndos[index].redo();
    }
  }

  // Undo.
  undo() {
    for (var index in self.childUndos) {
      self.childUndos[index].undo();
    }
  }
}

// Undo class for adding a person.
class UndoStack {
  // Constructor.
  constructor() {
    this.stack = [];
    this.index = -1;
    this.currentBlock = null;
    this.cleanIndex = -1;
  }

  // Add.
  add(undo) {
    // Add to block if it exists.
    if (this.currentBlock && (undo != this.currentBlock)) {
       this.currentBlock.add(undo);
       return;
    }

    // Clear from here to end.
    for (var i = this.index + 1; i < this.stack.length; ++i) {
       this.stack.pop()
    }

    // Add the item.
    this.stack.push(undo);

    // Update the index.
    this.index += 1;
  }

  // Begin an undo block.
  beginBlock() {
    this.currentBlock = UndoBlock()
  }

  // End an undo block.
  endBlock() {
    if (this.currentBlock && !this.currentBlock.isEmpty()) {
      this.add(this.currentBlock);
      this.currentBlock = null;
    }
  }

  // Clear the undo stack.
  clear() {
    this.stack = [];
    this.index = -1;
  }

  // Redo.
  redo() {
    var redoIndex = this.index + 1;

    if (redoIndex < this.stack.length) {
      console.log("About to redo from stack:", this.stack[redoIndex]);
      this.stack[redoIndex].redo();
      this.index += 1;
    }
    else {
      console.log("Nothing to redo.");
    }
  }

  // Undo.
  undo() {
    if (this.index >= 0) {
      this.stack[this.index].undo();
      this.index -= 1;
    }
    else {
      console.log("Nothing to undo.");
    }
  }

  // Check if unsaved changes exist.
  unsavedChangesExist() {
    return this.index == this.cleanIndex;
  }

  // Set the current index to clean.
  markSaved() {
    this.cleanIndex = this.index;
  }
}

// Undo stack.
var undoStack = new UndoStack();

// Add an undo item to the stack.
// function addUndo(item) {
//   undoStack.add(item);
// }

// Redo an action.
function redo() {
  console.log("Redo function called.");
  undoStack.redo();
  hideActiveMenu(); // Should be in upper level function?
}

// Undo an action.
function undo() {
  undoStack.undo();
  hideActiveMenu(); // Should be in upper level function?
}

// Hack: use global variable.
var _unsavedChangesExist = false;

function addUndo(item) {
  _unsavedChangesExist = true;

  if (item) {
    undoStack.add(item);
  }
}

// Mark as saved.
function markSaved() {
  // undoStack.markSaved();
  _unsavedChangesExist = false;
}

// Check if unsaved changes exist.
function unsavedChangesExist() {
  // return undoStack.unsavedChangesExist();
  return _unsavedChangesExist;
}

// -----------------------------------------------------------------------------
// Undo classes.
// -----------------------------------------------------------------------------

class AddPersonUndo {
  constructor(person) {
    this.person = person;
  }

  undo() {
    selectPerson(this.person);
    deleteSelectedItem();
  }

  redo () {
    // Add to canvas again.
    layer.add(this.person.group);

    // Add to dictionary.
    persons[this.person.personId] = this.person;

    // Add to tree view again.
    addPersonToTreeView(this.person);
  }
}

class DeletePersonUndo {
  constructor(person) {
    this.person = person;

    // Store relationships.
    this.relationships = person.relationships.slice(); // Copy array.
  }

  undo() {
    // Add to canvas again.
    layer.add(this.person.group);

    // Add to tree view again.
    addPersonToTreeView(this.person);

    // Add to dictionary.
    persons[this.person.personId] = this.person;

    // Add relationships again.
    for (var index in this.relationships) {
      // Perhaps store a DeleteRelationshipUndo as a child object?
      var relationship = this.relationships[index];
      undoDeleteRelationship(relationship);
    }
  }

  redo () {
    selectPerson(this.person);
    deleteSelectedItem();
  }
}

class AddRelationshipUndo {
  constructor(relationship) {
    this.relationship = relationship;
  }

  undo() {
    console.log("Undo add relationship.");

    selectRelationship(this.relationship);
    deleteSelectedItem();
  }

  redo() {
    console.log("Redo add relationship.");

    // Add to canvas again.
    layer.add(this.relationship.arrow);

    // Add to dictionary.
    relationships.push(this.relationship);

    // Add relationships to persons.
    persons[this.relationship.fromPersonId].relationships.push(this.relationship);
    persons[this.relationship.toPersonId].relationships.push(this.relationship);

    // Draw.
    updateArrowEndPoints(this.relationship);
  }
}

// Perhaps extract function here?
function undoDeleteRelationship(relationship) {
  // Add to canvas again.
  layer.add(relationship.arrow);

  // Add to dictionary.
  relationships.push(relationship);

  console.log("Relationship:", relationship.fromPersonId, "-->", relationship.toPersonId);

  // Add relationships to persons involved.
  // TODO: Need to differentiate between persons and sub-orgs here somehow
  // so we choose the right dictionary! How?
  if (relationship.fromPersonId in persons) {
    persons[relationship.fromPersonId].relationships.push(relationship);
  }
  else {
    subOrgs[relationship.fromPersonId].relationships.push(relationship);
  }

  // Hmm... What are the odds that the same ID could be in both
  // dictionaries?
  // Let's just make a design decision to assume that this won't happen!
  if (relationship.toPersonId in persons) {
    persons[relationship.toPersonId].relationships.push(relationship);
  }
  else {
    subOrgs[relationship.toPersonId].relationships.push(relationship);
  }
}

class DeleteRelationshipUndo {
  constructor(relationship) {
    this.relationship = relationship;
  }

  undo() {
    // Add to canvas again.
    layer.add(this.relationship.arrow);

    // Add to dictionary.
    relationships.push(this.relationship);

    // Add relationships to persons.
    persons[this.relationship.fromPersonId].relationships.push(this.relationship);
    persons[this.relationship.toPersonId].relationships.push(this.relationship);
  }

  redo () {
    selectRelationship(this.relationship);
    deleteSelectedItem();
  }
}

class EditPersonDetailsUndo {
  constructor(person) {
    this.person = person;

    this.oldName = person.name;
    this.oldTitle = person.title;
    this.oldURL = person.url;
    this.oldDepartment = person.department;
    this.oldPhotos = person.photos;
    this.oldActivePhotoIndex = person.activePhotoIndex;
    this.oldBorderColor = person.borderColor;
    this.oldFillColor = person.fillColor;
  }

  setAfterState(person) {
    this.newName = person.name;
    this.newTitle = person.title;
    this.newURL = person.url;
    this.newDepartment = person.department;
    this.newPhotos = person.photos;
    this.newActivePhotoIndex = person.activePhotoIndex;
    this.newBorderColor = person.borderColor;
    this.newFillColor = person.fillColor;
  }

  setOriginalPhotosList(photos) {
    this.oldPhotos = photos;
  }

  undo() {
    this.person.name = this.oldName;
    this.person.title = this.oldTitle;
    this.person.url = this.oldURL;
    this.person.department = this.oldDepartment;
    this.person.photos = this.oldPhotos;
    this.person.activePhotoIndex = this.oldActivePhotoIndex;
    this.person.borderColor = this.oldBorderColor;
    this.person.fillColor = this.oldFillColor;

    updatePersonBoxAndTreeViewEntry( this.person );
    updateThumbnail( this.person );
    restoreBorderColor( this.person );
    restoreFillColor( this.person );
  }

  redo () {
    this.person.name = this.newName;
    this.person.title = this.newTitle;
    this.person.url = this.newURL;
    this.person.department = this.newDepartment;
    this.person.photos = this.newPhotos;
    this.person.activePhotoIndex = this.newActivePhotoIndex;
    this.person.borderColor = this.newBorderColor;
    this.person.fillColor = this.newFillColor;

    updatePersonBoxAndTreeViewEntry( this.person );
    updateThumbnail( this.person );
    restoreBorderColor( this.person );
    restoreFillColor( this.person );
  }
}

class MovePersonUndo {
  constructor(person) {
    this.person = person;

    this.oldX = person.group.x();
    this.oldY = person.group.y();

    this.oldPositions = {};
    this.newPositions = {};
    this.oldPositionsSubOrgs = {};
    this.newPositionsSubOrgs = {};

    for (var personId in persons) {
      // Should narrow this down to selected persons only?
      this.oldPositions[personId] = persons[personId].group.position();
    }
    // TODO: Add sub-orgs.
    for (var subOrgId in subOrgs) {
      this.oldPositionsSubOrgs[subOrgId] = subOrgs[subOrgId].group.position();
    }
  }

  setAfterState() {
    this.newX = this.person.group.x();
    this.newY = this.person.group.y();

    for (var personId in persons) {
      // Should narrow this down to selected persons only?
      this.newPositions[personId] = persons[personId].group.position();
    }
    // TODO: Add sub-orgs.
    for (var subOrgId in subOrgs) {
      this.newPositionsSubOrgs[subOrgId] = subOrgs[subOrgId].group.position();
    }
  }

  undo() {
    this.person.group.x( this.oldX );
    this.person.group.y( this.oldY );
    updateRelationshipEndPoints(this.person);

    for (var personId in persons) {
      // Should narrow this down to selected persons only?
      var person = persons[personId];
      person.group.position(this.oldPositions[personId]);
      updateRelationshipEndPoints(person);
    }
    // TODO: Add sub-orgs.
    for (var subOrgId in subOrgs) {
      var subOrg = subOrgs[subOrgId];
      subOrg.group.position(this.oldPositionsSubOrgs[subOrgId]);
      updateRelationshipEndPoints(subOrg);
    }
  }

  redo () {
    this.person.group.x( this.newX );
    this.person.group.y( this.newY );
    updateRelationshipEndPoints(this.person);

    for (var personId in persons) {
      // Should narrow this down to selected persons only?
      var person = persons[personId];
      person.group.position(this.newPositions[personId]);
      updateRelationshipEndPoints(person);
    }
    // TODO: Add sub-orgs.
    for (var subOrgId in subOrgs) {
      var subOrg = subOrgs[subOrgId];
      subOrg.group.position(this.newPositionsSubOrgs[subOrgId]);
      updateRelationshipEndPoints(subOrg);
    }
  }
}

// Undo item for the current move operation.
var currentMoveUndoItem = null;

class AutoLayoutUndo {
  constructor() {
    this.oldPositions = {};
    this.newPositions = {};
    this.oldPositionsSubOrgs = {};
    this.newPositionsSubOrgs = {};

    for (var personId in persons) {
      this.oldPositions[personId] = persons[personId].group.position();
    }
    // TODO: Add sub-orgs.
    for (var subOrgId in subOrgs) {
      this.oldPositionsSubOrgs[subOrgId] = subOrgs[subOrgId].group.position();
    }
  }

  setAfterState() {
    for (var personId in persons) {
      // Index is also the person ID so use that directly.
      this.newPositions[personId] = persons[personId].group.position();
    }
    // TODO: Add sub-orgs.
    for (var subOrgId in subOrgs) {
      this.newPositionsSubOrgs[subOrgId] = subOrgs[subOrgId].group.position();
    }
  }

  undo() {
    for (var personId in persons) {
      var person = persons[personId];
      person.group.position(this.oldPositions[personId]);
      updateRelationshipEndPoints(person);
    }
    // TODO: Add sub-orgs.
    for (var subOrgId in subOrgs) {
      var subOrg = subOrgs[subOrgId];
      subOrg.group.position(this.oldPositionsSubOrgs[subOrgId]);
      updateRelationshipEndPoints(subOrg);
    }
  }

  redo () {
    for (var personId in persons) {
      var person = persons[personId];
      person.group.position(this.newPositions[personId]);
      updateRelationshipEndPoints(person);
    }
    // TODO: Add sub-orgs.
    for (var subOrgId in subOrgs) {
      var subOrg = subOrgs[subOrgId];
      subOrg.group.position(this.newPositionsSubOrgs[subOrgId]);
      updateRelationshipEndPoints(subOrg);
    }
  }
}

class SetBorderColorUndo {
  constructor(person, originalColor) {
    this.person = person;
    this.originalColor = originalColor;
    this.newColor = person.borderColor;
  }

  undo() {
    this.person.borderColor = this.originalColor;
    restoreBorderColor(this.person);
  }

  redo () {
    this.person.borderColor = this.newColor;
    restoreBorderColor(this.person);
  }
}

class AddSubOrgUndo {
  constructor(subOrg) {
    this.subOrg = subOrg;
  }

  undo() {
    console.log("Undo add sub-org.");
    selectSubOrg(this.subOrg);
    deleteSelectedItem();
  }

  redo () {
    // Add to canvas again.
    layer.add(this.subOrg.group);

    // Add to dictionary.
    subOrgs[this.subOrg.id] = this.subOrg;

    // Add to tree view again.
    // addPersonToTreeView(this.subOrg);
  }
}

class DeleteSubOrgUndo {
  constructor(subOrg) {
    this.subOrg = subOrg;

    // Store relationships.
    this.relationships = subOrg.relationships.slice(); // Copy array.
  }

  undo() {
    // Add to canvas again.
    layer.add(this.subOrg.group);

    // Add to tree view again.
    // addPersonToTreeView(this.person);

    // Add to dictionary.
    subOrgs[this.subOrg.id] = this.subOrg;

    // Add relationships again.
    for (var index in this.relationships) {
      // Perhaps store a DeleteRelationshipUndo as a child object?
      var relationship = this.relationships[index];
      undoDeleteRelationship(relationship);
    }
  }

  redo () {
    selectSubOrg(this.subOrg);
    deleteSelectedItem();
  }
}

class EditSubOrgDetailsUndo {
  constructor(subOrg) {
    this.subOrg = subOrg;

    this.oldName = subOrg.name;
    this.oldDiagramId = subOrg.diagramId;
  }

  setAfterState(subOrg) {
    this.newName = subOrg.name;
    this.newDiagramId = subOrg.diagramId;
  }

  undo() {
    this.subOrg.name = this.oldName;
    this.subOrg.diagramId = this.oldDiagramId;

    currentSubOrg.text.text( this.subOrg.name );
    updateSubOrgBoxToFitName( this.subOrg );
  }

  redo () {
    this.subOrg.name = this.newName;
    this.subOrg.diagramId = this.newDiagramId;

    currentSubOrg.text.text( this.subOrg.name );
    updateSubOrgBoxToFitName( this.subOrg );
  }
}

class ImportCSVUndo {
  constructor(personList) {
    this.personList = personList;
  }

  undo() {
    console.log("Person list:", this.personList);
    for (var personId in this.personList) {
      console.log("Person ID:", personId);
      var person = this.personList[personId];
      deletePerson(person);
    }
  }

  redo () {
    for (var personId in this.personList) {
      var person = this.personList[personId];

      // Add to canvas again.
      layer.add(person.group);

      // Add to tree view again.
      addPersonToTreeView(person);

      // TODO: Add relationships again.

      // TODO: Add person to dictionary again! Should really make a
      // separate function for this...
    }
  }
}
