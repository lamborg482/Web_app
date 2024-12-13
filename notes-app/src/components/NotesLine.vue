<template>
    <div class="notes-container">
        <div class="sidebar">
            <div class="top-panel">
                <button @click="showAddNote" class="add-button">Добавить</button>
                <button @click="deleteNote" class="delete-button" :disabled="!selectedNote?.id" v-if="selectedNote?.id">Удалить</button>
            </div>
            <div class="divider"></div>
            <ul class="notes-list">
                <li v-for="note in notes" :key="note.id" @click="selectNote(note)" class="note-item" :class="{ active: selectedNote?.id === note.id }">
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
                <div class="all-img">
                    <label class="custom-file-upload"> Прикрепить изображение <input type="file" @change="onFileChange" multiple :disabled="previewImages.length >= 3"> </label>
                    <div v-for="(image, index) in previewImages" :key="index" class="note-image-preview-container">
                        <img :src="image" alt="Image Preview" class="note-image-preview">
                        <button @click="removeImage(index)" class="remove-button">Удалить</button>
                    </div>
                </div>
                <div class="buttons">
                    <button @click="addNoteWithImage" class="save-button">Сохранить</button>
                </div>
            </div>
            <div v-else-if="selectedNote?.title" class="contnotes">
                <textarea v-model="selectedNote.title" class="note-input" placeholder="Название" required></textarea>
                <div class="note-divider"></div>
                <textarea v-model="selectedNote.description" class="note-textarea" placeholder="Описание"></textarea>
                <div class="note-divider"></div>
                <div v-for="(url, index) in selectedNote?.image_urls || []" :key="index" class="note-image-container">
                    <img :src="url" alt="Note Image" class="note-image">
                    <button @click="deleteImage(index)" class="remove-button">Удалить</button>
                </div>
                <div class="all-img">
                    <label class="custom-file-upload"> Прикрепить изображение <input type="file" @change="onFileChange" multiple :disabled="previewImages.length >= 3"> </label>
                    <div v-for="(image, index) in previewImages" :key="index" class="note-image-preview-container">
                        <img :src="image" alt="Image Preview" class="note-image-preview">
                        <button @click="removeImage(index)" class="remove-button">Удалить</button>
                    </div>
                </div>
                <div class="buttons">
                    <button @click="updateNoteWithImage" class="save-button">Сохранить</button>
                </div>
            </div>
            <div v-else>
                Выберите заметку для просмотра её содержания
            </div>
        </div>
    </div>
</template>

<script>
import { useNoteStore } from '@/store/noteStore';
import { onMounted, ref } from 'vue';
import api from '../api';

export default {
    setup() {
        const noteStore = useNoteStore();
        const { notes, isAddingNote, newTitle, newDescription, fetchNotes, deleteNote, showAddNote } = noteStore;
        const selectedNote = ref({});

        let files = [];
        const previewImages = ref([]);

        const onFileChange = (event) => {
            const newFiles = Array.from(event.target.files);
            if (files.length + newFiles.length > 3) {
                alert('Maximum 3 images allowed');
                return;
            }
            files = [...files, ...newFiles];
            newFiles.forEach(file => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImages.value.push(e.target.result);
                };
                reader.readAsDataURL(file);
            });
        };

        const removeImage = (index) => {
            files.splice(index, 1);
            previewImages.value.splice(index, 1);
        };

        const addNoteWithImage = async () => {
            if (!newTitle.value || !newDescription.value) {
                console.error("Title or Description is empty!");
                return;
            }
            try {
                const noteData = new FormData();
                noteData.append('title', newTitle.value);
                noteData.append('description', newDescription.value);
                files.forEach(file => {
                    noteData.append('files', file);
                });
                await api.addNoteWithImage(noteData);
                newTitle.value = '';
                newDescription.value = '';
                isAddingNote.value = false;
                files = [];
                previewImages.value = [];
                await fetchNotes();
            } catch (error) {
                console.error("Error adding note:", error);
            }
        };

        const updateNoteWithImage = async () => {
            if (!selectedNote.value || !selectedNote.value.title || !selectedNote.value.description) {
                console.error("Selected note is not properly defined!");
                return;
            }
            try {
                const noteData = new FormData();
                noteData.append('title', selectedNote.value.title);
                noteData.append('description', selectedNote.value.description);
                files.forEach(file => {
                    noteData.append('files', file);
                });
                await api.updateNote(selectedNote.value.id, noteData);
                files = [];
                previewImages.value = [];
                await fetchNotes();
            } catch (error) {
                console.error("Error updating note:", error);
            }
        };

        const deleteImage = async (index) => {
            if (!selectedNote.value.image_urls) {
                console.error("Selected note or its image_urls are not properly defined!");
                return;
            }
            const newImageUrls = [...selectedNote.value.image_urls];
            newImageUrls.splice(index, 1);
            await api.updateNote(selectedNote.value.id, {
                ...selectedNote.value,
                image_urls: newImageUrls
            });
            selectedNote.value.image_urls = newImageUrls;
            files = [];
            previewImages.value = [];
            await fetchNotes();
        };

        const selectNote = (note) => {
            if (!note) {
                console.error("Note is not properly defined!");
                return;
            }
            if (!note.image_urls) {
                note.image_urls = [];
            }
            selectedNote.value = note;
            console.log("Selected note:", selectedNote.value);
        };

        onMounted(() => {

            console.log("Current notes:", notes.value);
        });

        return {
            notes,
            selectedNote,
            isAddingNote,
            newTitle,
            newDescription,
            addNoteWithImage,
            updateNoteWithImage,
            selectNote,
            deleteNote,
            showAddNote,
            onFileChange,
            previewImages,
            removeImage,
            deleteImage,
        };
    },
};
</script>

<style lang="css" scoped>
@import url('/src/assets/style.css');
</style>
