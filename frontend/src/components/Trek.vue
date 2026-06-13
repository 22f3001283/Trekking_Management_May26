<template>
    <div class="container mt-4">
        <form @submit.prevent="handleSubmit" class="row g-3">
            <div class="col-12">
                <h3 v-if="mode==='create'">Create Trek</h3>
                <h3 v-else-if="mode==='edit'">Edit Trek</h3>
                <h3 v-else>View Trek</h3>
            </div>

            <div class="col-md-6">
                <label for="trek_name" class="form-label">Trek Name</label>
                <input v-model="form.trek_name" :disabled="isView" type="text" class="form-control" id="trek_name" required>
            </div>

            <div class="col-md-6">
                <label for="location" class="form-label">Location</label>
                <input v-model="form.location" :disabled="isView" type="text" class="form-control" id="location" required>
            </div>

            <div class="col-md-4">
                <label for="difficulty" class="form-label">Difficulty</label>
                <select v-model="form.difficulty" :disabled="isView" id="difficulty" class="form-select" required>
                    <option value="Easy">Easy</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Hard">Hard</option>
                </select>
            </div>

            <div class="col-md-4">
                <label for="duration_display" class="form-label">Duration (days)</label>
                <input type="text" class="form-control" id="duration_display" :value="calculatedDuration" disabled>
            </div>

            <div class="col-md-4">
                <label for="available_slots" class="form-label">Available Slots</label>
                <input v-model.number="form.available_slots" :disabled="isView" type="number" min="0" class="form-control" id="available_slots" required>
            </div>

            <div class="col-md-4">
                <label for="price" class="form-label">Price (per person)</label>
                <input v-model.number="form.price" :disabled="isView" type="number" step="0.01" min="0" class="form-control" id="price" required>
            </div>

            <div class="col-md-4">
                <label for="assigned_staff_id" class="form-label">Assign Staff</label>
                <select v-model.number="form.assigned_staff_id" :disabled="isView" id="assigned_staff_id" class="form-select" required>
                    <option value="">-- Select Staff --</option>
                    <option v-for="staff in availableStaff" :key="staff.user_id" :value="staff.user_id">
                        {{ staff.user_id }} - {{ staff.username }}
                    </option>
                </select>
            </div>

            <div class="col-md-4">
                <label for="status" class="form-label">Status</label>
                <select v-model="form.status" :disabled="isView" id="status" class="form-select">
                    <option value="Pending">Pending</option>
                    <option value="Approved">Approved</option>
                    <option value="Open">Open</option>
                    <option value="Closed">Closed</option>
                    <option value="Completed">Completed</option>
                    <option value="Cancelled">Cancelled</option>
                </select>
            </div>

            <div class="col-md-6">
                <label for="start_date" class="form-label">Start Date</label>
                <input v-model="form.start_date" :disabled="isView" type="date" class="form-control" id="start_date" required :min="todayString">
            </div>

            <div class="col-md-6">
                <label for="end_date" class="form-label">End Date</label>
                <input v-model="form.end_date" :disabled="isView" type="date" class="form-control" id="end_date" required :min="endDateMin">
            </div>

            <div class="col-md-6">
                <label class="form-label">Upload Images</label>
                
                <div class="d-flex flex-wrap gap-2 mb-2">
                    <div 
                        v-for="(img, index) in imagePreviews" 
                        :key="index" 
                        style="position: relative; width: 80px; height: 80px;"
                    >
                        <img :src="img" style="width: 80px; height: 80px; object-fit: cover; border-radius: 6px;">
                        <button 
                            v-if="!isView"
                            type="button" 
                            @click="removeImage(index)"
                            style="position: absolute; top: -6px; right: -6px; width: 20px; height: 20px; border-radius: 50%; background: red; color: white; border: none; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center;"
                        >×</button>
                    </div>
                </div>

                <input 
                    v-if="!isView"
                    class="form-control" 
                    type="file" 
                    ref="fileInput" 
                    multiple 
                    @change="handleFileChange"
                >
            </div>
            
            <div class="col-12">
                <p v-if="trek && trek.average_rating">Average rating: {{ trek.average_rating }}</p>
                <p v-else-if="trek">No ratings</p>
            </div>

            <div class="col-12 text-center mt-3">
                <button v-if="!isView" type="submit" class="btn btn-primary me-2" style="background-color: #9e52eb;">{{ mode==='create' ? 'Create Trek' : 'Save Changes' }}</button>
                <button type="button" class="btn btn-secondary" @click="handleCancel" style="background-color: #818285;">{{ isView ? 'Close' : 'Cancel' }}</button>
            </div>
        </form>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'Trek',
    props: {
        mode: { type: String, default: 'create' }, // create | edit | view
        trek: { type: Object, default: null }
    },
    data() {
        return {
            form: {
                trek_name: '',
                location: '',
                difficulty: 'Easy',
                available_slots: 0,
                price: 0.0,
                assigned_staff_id: null,
                status: 'Pending',
                start_date: '',
                end_date: ''
            },
            availableStaff: [],
            images: [],
            isSubmitting: false,
            imagePreviews: []
        }
    },
    computed: {
        isView() { return this.mode === 'view' },
        todayString() {
            const today = new Date()
            const offset = today.getTimezoneOffset()
            const local = new Date(today.getTime() - offset * 60000)
            return local.toISOString().slice(0, 10)
        },
        endDateMin() {
            return this.form.start_date || this.todayString
        },
        calculatedDuration() {
            if (!this.form.start_date || !this.form.end_date) return '0'
            const start = new Date(this.form.start_date)
            const end = new Date(this.form.end_date)
            const diff = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
            return Math.max(1, diff)
        }
    },
    watch: {
        trek: {
            immediate: true,
            handler(t) {
                if (!t) return
                this.form.trek_name = t.trek_name || ''
                this.form.location = t.location || ''
                this.form.difficulty = t.difficulty || 'Easy'
                this.form.available_slots = t.available_slots || 0
                this.form.price = t.price || 0.0
                this.form.assigned_staff_id = t.assigned_staff_id ? parseInt(t.assigned_staff_id) : null
                this.form.status = t.status || 'Pending'
                this.form.start_date = t.start_date ? t.start_date.slice(0,10) : ''
                this.form.end_date = t.end_date ? t.end_date.slice(0,10) : ''
                this.imagePreviews = (t.images || []).filter(img => img.startsWith('data:'))
            }
        }
    },
    methods: {
        async fetchStaff() {
            try {
                const token = localStorage.getItem('token')
                const response = await axios.get('http://127.0.0.1:5000/users', {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                this.availableStaff = response.data.filter(user => user.role === 'staff' && user.status === 'active')
            } catch (error) {
                console.error('Error fetching staff:', error)
            }
        },

        async handleSubmit() {
            console.log("handleSubmit called", new Date().toISOString())
            if (this.isSubmitting) return   // ← prevents double fire
            this.isSubmitting = true

            const today = new Date()
            today.setHours(0, 0, 0, 0)
            const startDate = new Date(this.form.start_date)
            startDate.setHours(0, 0, 0, 0)
            const endDate = new Date(this.form.end_date)
            endDate.setHours(0, 0, 0, 0)

            if (startDate < today) {
                alert('Start date cannot be before today')
                this.isSubmitting = false
                return
            }

            if (endDate < startDate) {
                alert('End date cannot be before start date')
                this.isSubmitting = false
                return
            }

            if (!this.form.assigned_staff_id) {
                alert('Please select a staff member')
                this.isSubmitting = false
                return
            }

            const images = this.imagePreviews
            const payload = {
                ...this.form,
                duration_days: this.calculatedDuration,
                images
            }
            this.$emit('submit', payload)
            this.isSubmitting = false
        },
        handleCancel() {
            this.$emit('cancel')
        },
        handleFileChange(event) {
            const files = Array.from(event.target.files)
            files.forEach(file => {
                const reader = new FileReader()
                reader.onload = (e) => {
                    this.imagePreviews.push(e.target.result)
                }
                reader.readAsDataURL(file)
            })
        },
        removeImage(index) {
            this.imagePreviews.splice(index, 1)
        },
    },
    mounted() {
        this.fetchStaff()
    }
}
</script>
<style scoped>
.btn-primary, .btn-secondary {
    opacity: 1 !important;
}
input[type="date"]::-webkit-calendar-picker-indicator {
    display: block;
    opacity: 1;
    cursor: pointer;
    width: 20px;
    height: 20px;
}
</style>
