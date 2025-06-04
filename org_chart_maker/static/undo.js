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
  }

  undo() {
    // Add to canvas again.
    layer.add(this.person.group);

    // Add to tree view again.
    addPersonToTreeView(this.person);

    // TODO: Add relationships again.
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
  }

  setAfterState(person) {
    this.newName = person.name;
    this.newTitle = person.title;
    this.newURL = person.url;
    this.newDepartment = person.department;
    this.newPhotos = person.photos;
    this.newActivePhotoIndex = person.activePhotoIndex;
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

    updatePersonBoxAndTreeViewEntry( this.person );
    updateThumbnail( this.person );
  }

  redo () {
    this.person.name = this.newName;
    this.person.title = this.newTitle;
    this.person.url = this.newURL;
    this.person.department = this.newDepartment;
    this.person.photos = this.newPhotos;
    this.person.activePhotoIndex = this.newActivePhotoIndex;

    updatePersonBoxAndTreeViewEntry( this.person );
    updateThumbnail( this.person );
  }
}

class MovePersonUndo {
  constructor(person) {
    this.person = person;

    this.oldX = person.group.x();
    this.oldY = person.group.y();
  }

  setAfterState() {
    this.newX = this.person.group.x();
    this.newY = this.person.group.y();
  }

  undo() {
    this.person.group.x( this.oldX );
    this.person.group.y( this.oldY );
    updateRelationshipEndPoints(this.person);
  }

  redo () {
    this.person.group.x( this.newX );
    this.person.group.y( this.newY );
    updateRelationshipEndPoints(this.person);
  }
}

// Undo item for the current move operation.
var currentMoveUndoItem = null;

class AutoLayoutUndo {
  constructor() {
    this.oldPositions = {};
    this.newPositions = {};

    for (var personId in persons) {
      this.oldPositions[personId] = persons[personId].group.position();
    }
  }

  setAfterState() {
    for (var personId in persons) {
      // Index is also the person ID so use that directly.
      this.newPositions[personId] = persons[personId].group.position();
    }
  }

  undo() {
    for (var personId in persons) {
      var person = persons[personId];
      person.group.position(this.oldPositions[personId]);
      updateRelationshipEndPoints(person);
    }
  }

  redo () {
    for (var personId in persons) {
      var person = persons[personId];
      person.group.position(this.newPositions[personId]);
      updateRelationshipEndPoints(person);
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
