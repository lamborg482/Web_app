<template>
    <div class="notes-container">
        <div class="sidebar">

            <div class="top-panel">
                <button @click="showAddNote" class="add-button">Добавить</button>
                <button @click="deleteNote(selectedNote)" class="delete-button" :disabled="!selectedNote" v-if="selectedNote">Удалить</button>
            </div>
            <div class="divider"></div>
            <ul class="notes-list">
                <li v-for="note in notes" :key="note.id" @click="selectNote(note)" class="note-item" :class="{ active: selectedNote && selectedNote.id === note.id }">
                    <h2 class="note-title">{{ note.title.length > 25 ? note.title.substring(0, 25) + '...' : note.title }}</h2>
                    <h3>{{ note.created_at }}</h3>
                    <div class="note-divider"></div>
                </li>
            </ul>
        </div>
        <div class="content">
            <div v-if="isAddingNote" class="cont_notes">
                <div class="cont_notes">
                    <h3>Создать новую заметку</h3>
                    <textarea v-model="newTitle" placeholder="Название" required class="note-input" ></textarea>
                    <textarea v-model="newDescription" placeholder="Описание" required class="note-textarea"></textarea>
                    <div class="buttons">
                        <button @click="addNote" class="save-button">Сохранить</button>
                    </div>
                </div>
            </div>
            <div v-else-if="selectedNote" class="cont_notes">
                <div class="cont_notes">
                    <textarea v-model="selectedNote.title" class="note-input" placeholder="Название" required ></textarea>
                    <div class="note-divider"></div> 
                    <textarea v-model="selectedNote.description" class="note-textarea" placeholder="Описание"></textarea>
                    <div class="note-divider"></div> 
                </div>
            </div>
            <div v-else>
                <h3>Выберите заметку для просмотра её содержания</h3>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import { ref, onMounted, watch } from "vue";

export default {
    setup() {
        const notes = ref([]);
        const selectedNote = ref(null);
        const isAddingNote = ref(false);
        const newTitle = ref('');
        const newDescription = ref('');

        const fetchNotes = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/notes/`);
                notes.value = response.data;
            } catch (error) {
                console.error("Error fetching notes:", error);
            }
        };

        const addNote = async () => {
            try {
                await axios.post(`http://localhost:8000/notes/`, {
                    title: newTitle.value,
                    description: newDescription.value
                });
                newTitle.value = '';
                newDescription.value = '';
                isAddingNote.value = false;
                fetchNotes();
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
                await axios.delete(`http://localhost:8000/notes/${note.id}`);
                fetchNotes();
                selectedNote.value = null;
            } catch (error) {
                console.error("Error deleting note:", error);
            }
        };

        const showAddNote = () => {
            isAddingNote.value = true;
            selectedNote.value = null; 
        };

        watch(selectedNote, (note) => {
            if (note) {
                autoSave(note);
            }
        });

        const autoSave = async (note) => {
            if (note) {
                try {
                    await axios.put(`http://localhost:8000/notes/${note.id}`, {
                        title: note.title,
                        description: note.description
                    });
                } catch (error) {
                    console.error("Error updating note:", error);
                }
            }
        };

        onMounted(fetchNotes);

        return {
            notes,
            selectedNote,
            isAddingNote,
            newTitle,
            newDescription,
            addNote,
            selectNote,
            deleteNote,
            showAddNote
        };
    },
};
</script>

<style lang="css" scoped>
@import url('/src/assets/style.css');
</style>