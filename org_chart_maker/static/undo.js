// =============================================================================
// Undo framework.
// =============================================================================

// // Undo block class.
// class UndoBlock {
//   // Constructor.
//   constructor() {
//     this.childUndos = [];
//   }
//
//   // Add an item.
//   add(item) {
//     this.childUndos.push(item);
//   }
//
//   // Check if empty.
//   isEmpty() {
//     return this.childUndos.length == 0;
//   }
//
//   // Redo.
//   redo() {
//     for (var index in self.childUndos) {
//       self.childUndos[index].redo();
//     }
//   }
//
//   // Undo.
//   undo() {
//     for (var index in self.childUndos) {
//       self.childUndos[index].undo();
//     }
//   }
// }
//
// // Undo class for adding a person.
// class UndoStack {
//   // Constructor.
//   constructor() {
//     this.stack = [];
//     this.index = -1;
//     this.currentBlock = null;
//     this.cleanIndex = -1;
//   }
//
//   // Add.
//   add(undo) {
//     // Add to block if it exists.
//     if (this.currentBlock && (undo != this.currentBlock)) {
//        this.currentBlock.add(undo);
//        return;
//     }
//
//     // Clear from here to end.
//     for (var i = this.index + 1; i < this.stack.length; ++i) {
//        this.stack.pop()
//     }
//
//     // Add the item.
//     this.stack.push(undo);
//
//     // Update the index.
//     this.index += 1;
//   }
//
//   // Begin an undo block.
//   beginBlock() {
//     this.currentBlock = UndoBlock()
//   }
//
//   // End an undo block.
//   endBlock() {
//     if (this.currentBlock && !this.currentBlock.isEmpty()) {
//       this.add(this.currentBlock);
//       this.currentBlock = null;
//     }
//   }
//
//   // Clear the undo stack.
//   clear() {
//     this.stack = [];
//     this.index = -1;
//   }
//
//   // Redo.
//   redo() {
//     var redoIndex = this.index + 1;
//
//     if (redoIndex < this.stack.length) {
//       this.stack[redoIndex].redo();
//       this.index += 1;
//     }
//     else {
//       console.log("Nothing to redo.");
//     }
//   }
//
//   // Undo.
//   undo() {
//     if (this.index >= 0) {
//       this.stack[this.index].undo();
//       this.index -= 1;
//     }
//     else {
//       console.log("Nothing to undo.");
//     }
//   }
//
//   // Check if unsaved changes exist.
//   unsavedChangesExist() {
//     return this.index == this.cleanIndex;
//   }
//
//   // Set the current index to clean.
//   markSaved() {
//     this.cleanIndex = this.index;
//   }
// }
//
// // Undo stack.
// var undoStack = new UndoStack();
//
// // Add an undo item to the stack.
// function addUndo(item) {
//   undoStack.add(item);
// }
//
// // Redo an action.
// function redo() {
//   undoStack.redo();
// }
//
// // Undo an action.
// function undo() {
//   undoStack.undo();
// }

// Hack: use global variable.
var _unsavedChangesExist = false;

function addUndo() {
  _unsavedChangesExist = true;
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
