import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default {
    async fetchNotes() {
        return apiClient.get('/notes/');
    },
    async addNoteWithImage(noteData) {
        return apiClient.post('/notes/', noteData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },
    async updateNote(noteId, noteData) {
        return apiClient.put(`/notes/${noteId}`, noteData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },
    async deleteNote(noteId) {
        return apiClient.delete(`/notes/${noteId}`);
    },
};
