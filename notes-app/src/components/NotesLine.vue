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
            <h2 class="note-title">{{ note.title.length > 25 ? note.title.substring(0, 25) + '…' : note.title }}</h2>
            <div class="note-divider"></div>
        </li>
        </ul>
    </div>
    <div class="content">
        <div v-if="isAddingNote" class="cont_notes">
        Создать новую заметку
        <textarea v-model="newTitle" placeholder="Название" required class="note-input"></textarea>
        <textarea v-model="newDescription" placeholder="Описание" required class="note-textarea"></textarea>
        <div class="buttons">
            <button @click="addNote" class="save-button">Сохранить</button>
        </div>
        </div>
        <div v-else-if="selectedNote" class="contnotes">
        <textarea v-model="selectedNote.title" class="note-input" placeholder="Название" required></textarea>
        <div class="note-divider"></div>
        <textarea v-model="selectedNote.description" class="note-textarea" placeholder="Описание"></textarea>
        <div class="note-divider"></div>
        </div>
        <div v-else>
        Выберите заметку для просмотра её содержания
        </div>
    </div>
    </div>
</template>

<script>
import { useNoteStore } from '@/store/noteStore';
import { onMounted } from 'vue';

export default {
    setup() {
    const noteStore = useNoteStore();
    const { notes, selectedNote, isAddingNote, newTitle, newDescription, fetchNotes, addNote, selectNote, deleteNote, showAddNote } = noteStore;
    
    onMounted(() => {
        fetchNotes();
        console.log("Current notes:", notes.value); 
    });

    return {
        notes,
        selectedNote,
        isAddingNote,
        newTitle,
        newDescription,
        addNote,
        selectNote,
        deleteNote,
        showAddNote,
    };
    },
};
</script>
    
<style lang="css" scoped>
@import url('/src/assets/style.css');
</style>
