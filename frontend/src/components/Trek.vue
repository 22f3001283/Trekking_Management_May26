<template>
    <div class="container mt-4">
        <form @submit.prevent="handleSubmit" class="row g-3">

            <div class="col-md-6">
                <label for="trek_name" class="form-label" v-if="mode==='view'">Trek Name</label>
                <label for="trek_name" class="form-label" v-else>Trek Name <span class="text-danger" style="text-align: right"><small>(required)</small></span></label>
                <input v-model="form.trek_name" :disabled="isView || isStatusLocked" type="text" class="form-control" id="trek_name" required>
            </div>

            <div class="col-md-6">
                <label for="location" class="form-label">Location</label>
                <input v-model="form.location" :disabled="isView || isStatusLocked" type="text" class="form-control" id="location" >
            </div>

            <div class="col-md-4">
                <label for="difficulty" class="form-label">Difficulty</label>
                <select v-model="form.difficulty" :disabled="isView || isStatusLocked" id="difficulty" class="form-select" >
                    <option value="" disabled>-- Select Difficulty --</option>
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
                <input v-model.number="form.available_slots" :disabled="isView || isStatusLocked" type="number" min="0" class="form-control" id="available_slots" >
            </div>

            <div class="col-md-4">
                <label for="price" class="form-label">Price (per person)</label>
                <input v-model.number="form.price" :disabled="isView || isStatusLocked" type="number" step="0.01" min="0" class="form-control" id="price" >
            </div>

            <div class="col-md-4">
                <label for="assigned_staff_id" class="form-label" v-if="mode==='view'">Assigned Staff</label>
                <label for="assigned_staff_id" class="form-label" v-else >Assign Staff</label>
                <select v-model.number="form.assigned_staff_id" :disabled="isView || isStatusLocked" id="assigned_staff_id" class="form-select" >
                    <option value="">-- Select Staff --</option>
                    <option v-for="staff in availableStaff" :key="staff.user_id" :value="staff.user_id">
                        {{ staff.user_id }} - {{ staff.username }}
                    </option>
                </select>
            </div>

            <div class="col-md-4">
                <label for="status" class="form-label" v-if="mode==='view'">Current Status</label>
                <label for="status" class="form-label" v-else >Status</label>                
                <select v-model="form.status" :disabled="isView || isStatusLocked" id="status" class="form-select">
                    <option value="Pending">Pending</option>
                    <option value="Approved">Approved</option>
                    <option value="Open">Open</option>
                    <option value="Closed">Closed</option>
                    <option value="Completed">Completed</option>
                    <option value="Cancelled">Cancelled</option>
                </select>
                <small v-if="isStatusLocked" class="text-danger d-block mt-1">
                    This trek is {{ trek.status }} and can no longer be edited.
                </small>
            </div>

            <div class="col-md-6">
                <label for="start_date" class="form-label">Start Date</label>
                <input v-model="form.start_date" :disabled="isView || isStatusLocked" type="date" class="form-control" id="start_date"  :min="tomorrowString">
            </div>

            <div class="col-md-6">
                <label for="end_date" class="form-label">End Date</label>
                <input v-model="form.end_date" :disabled="isView || isStatusLocked" type="date" class="form-control" id="end_date"  :min="endDateMin">
            </div>

            <div class="col-md-6">
                <label class="form-label" v-if="mode==='view'">Uploaded Images</label>
                <label class="form-label" v-else-if="mode==='edit'">Upload Images</label>
                <label class="form-label" v-else >Upload Images</label>

                <div class="d-flex flex-wrap gap-2 mb-2">
                    <div 
                        v-for="(img, index) in imagePreviews" 
                        :key="index" 
                        style="position: relative; width: 80px; height: 80px;"
                    >
                        <img :src="img" style="width: 80px; height: 80px; object-fit: cover; border-radius: 6px;">
                        <button 
                            v-if="!isView && !isStatusLocked"
                            type="button" 
                            @click="removeImage(index)"
                            style="position: absolute; top: -6px; right: -6px; width: 20px; height: 20px; border-radius: 50%; background: red; color: white; border: none; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center;"
                        >×</button>
                    </div>
                </div>

                <input 
                    v-if="!isView && !isStatusLocked"
                    class="form-control" 
                    type="file" 
                    ref="fileInput" 
                    multiple 
                    @change="handleFileChange"
                >
            </div>

            <div class="col-12 text-center mt-3">
                <button v-if="!isView && !isStatusLocked" type="submit" class="btn btn-primary me-2" style="background-color: #4169e1;">{{ mode==='create' ? 'Create Trek' : 'Save Changes' }}</button>
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
                difficulty: '',
                available_slots: null,
                price: null,
                assigned_staff_id: null,
                status: 'Pending',
                start_date: '',
                end_date: ''
            },
            availableStaff: [],
            images: [],
            isSubmitting: false,
            imagePreviews: [],
        }
    },
    computed: {
        isView() { return this.mode === 'view' },
        isStatusLocked() {
            return this.trek && (this.trek.status === 'Completed' || this.trek.status === 'Cancelled')
        },
        tomorrowString() {
            const tomorrow = new Date()
            const offset = tomorrow.getTimezoneOffset()
            const local = new Date(tomorrow.getTime() - offset * 60000)
            local.setDate(local.getDate() + 1)   // ← added
            return local.toISOString().slice(0, 10)
        },
        endDateMin() {
            return this.form.start_date || this.tomorrowString
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
                this.form.location = t.location ?? ''
                this.form.difficulty = t.difficulty ?? ''
                this.form.available_slots = t.available_slots ?? null
                this.form.price = t.price ?? null
                this.form.assigned_staff_id = t.assigned_staff_id ? parseInt(t.assigned_staff_id) : null
                this.form.status = t.status || 'Pending'
                this.form.start_date = t.start_date ? t.start_date.slice(0,10) : ''
                this.form.end_date = t.end_date ? t.end_date.slice(0,10) : ''
                this.imagePreviews = (t.images || []).filter(img => img.startsWith('data:'))
            },
        },
        'form.status'(newStatus, oldStatus) {
            if ((newStatus === 'Completed' || newStatus === 'Cancelled') && newStatus !== oldStatus) {
                alert(`Warning: Setting this trek's status to "${newStatus}" cannot be undone once saved.`)
            }
        }        
    },
    methods: {
        resetForm() {
            this.form = {
                trek_name: '',
                location: '',
                difficulty: '',
                available_slots: null,
                price: null,
                assigned_staff_id: null,
                status: 'Pending',
                start_date: '',
                end_date: ''
            }
            this.imagePreviews = []
            if (this.$refs.fileInput) {
                this.$refs.fileInput.value = null
            }
        },
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
            if (this.isSubmitting) return
            this.isSubmitting = true
            
            const tomorrow = new Date()
            tomorrow.setHours(0, 0, 0, 0)
            tomorrow.setDate(tomorrow.getDate() + 1)
            
            const startDate = new Date(this.form.start_date)
            startDate.setHours(0, 0, 0, 0)
            const endDate = new Date(this.form.end_date)
            endDate.setHours(0, 0, 0, 0)

            if (this.form.start_date && startDate < tomorrow) {
                alert('Start date must be tomorrow or later')
                this.isSubmitting = false
                return
            }

            if (this.form.start_date && this.form.end_date && endDate < startDate) {
                alert('End date cannot be before start date')
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
