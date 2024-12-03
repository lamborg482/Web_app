import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    headers: {
    'Content-Type': 'application/json',
    },
});

export default {
    async fetchNotes() {
        return apiClient.get('/notes/');
    },
    async addNote(note) {
        return apiClient.post('/notes/', note);
    },
    async deleteNote(noteId) {
        return apiClient.delete(`/notes/${noteId}`);
    },
};
