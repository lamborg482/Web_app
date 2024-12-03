import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../api';

export const useNoteStore = defineStore('note', () => {
const notes = ref([]);
const selectedNote = ref(null);
const isAddingNote = ref(false);
const newTitle = ref('');
const newDescription = ref('');

const fetchNotes = async () => {
    try {
    const response = await api.fetchNotes();
    notes.value = response.data;
    console.log("Fetched notes:", notes.value);
    } catch (error) {
    console.error("Error fetching notes:", error);
    }
};

const addNote = async () => {
    if (!newTitle.value || !newDescription.value) {
    console.error("Title or Description is empty!");
    return;
    }
    try {
    await api.addNote({
        title: newTitle.value,
        description: newDescription.value,
    });
    newTitle.value = '';
    newDescription.value = '';
    isAddingNote.value = false;
    await fetchNotes();
    } catch (error) {
    console.error("Error adding note:", error);
    }
};

const selectNote = (note) => {
    selectedNote.value = note;
    isAddingNote.value = false;
};

const deleteNote = async (note) => {
    if (!note) return;
    try {
    await api.deleteNote(note.id);
    await fetchNotes();
    selectedNote.value = null;
    } catch (error) {
    console.error("Error deleting note:", error);
    }
};

const showAddNote = () => {
    isAddingNote.value = true;
    selectedNote.value = null;
};

return {
    notes,
    selectedNote,
    isAddingNote,
    newTitle,
    newDescription,
    fetchNotes,
    addNote,
    selectNote,
    deleteNote,
    showAddNote,
};
});
