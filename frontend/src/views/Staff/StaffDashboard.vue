<template>
    <div class="container-fluid" style="margin-top: 70px;">
        <h1 class="text-center mb-4">Staff Dashboard</h1>
    </div>

    <div class="container-fluid" style="padding-left: 100px; padding-right: 100px;">
        <div class="d-flex gap-2 mb-3 align-items-right justify-content-end">

            <!-- Search -->
            <div class="input-group" style="max-width: 370px;">
                <input class="form-control" type="search" v-model="searchQuery" :placeholder="'Search by ' + searchField.replace('_', ' ') + '...'" aria-label="Search">
                <select class="form-select" v-model="searchField" style="max-width: 150px;">
                    <option value="trek_name">Trek Name</option>
                    <option value="location">Location</option>
                    <option value="difficulty">Difficulty</option>
                    <option value="status">Status</option>
                </select>
            </div>

            <!-- Sort -->
            <div class="dropdown">
                <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                    Sort
                </button>
                <div class="dropdown-menu p-3" style="min-width: 220px;">
                    <label class="form-label fw-bold">Sort By</label>
                    <select class="form-select" v-model="sortBy">
                        <option value="">None</option>
                        <option value="price_asc">Price: Low to High</option>
                        <option value="price_desc">Price: High to Low</option>
                        <option value="duration">Duration</option>
                    </select>
                </div>
            </div>

            <!-- Filter -->
            <div class="dropdown">
                <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                    Filter
                </button>
                <div class="dropdown-menu p-3" style="min-width: 280px;">
                    <label class="form-label fw-bold">Difficulty</label>
                    <select class="form-select mb-3" v-model="filterDifficulty">
                        <option value="">All</option>
                        <option value="Easy">Easy</option>
                        <option value="Moderate">Moderate</option>
                        <option value="Hard">Hard</option>
                    </select>

                    <label class="form-label fw-bold">Status</label>
                    <select class="form-select mb-3" v-model="filterStatus">
                        <option value="">All</option>
                        <option value="Open">Open</option>
                        <option value="Closed">Closed</option>
                        <option value="Completed">Completed</option>
                    </select>

                    <button class="btn btn-outline-danger w-100" @click="resetFilters">Reset Filters</button>
                </div>
            </div>

        </div>
    </div>

    <!-- Trek Cards -->
    <div id="trekPanel" style="padding-left: 100px; padding-right: 100px;">
        <h2>My Assigned Treks</h2>
        <div v-if="filteredTreks.length > 0" class="row g-4">
            <div v-for="trek in filteredTreks" :key="trek.trek_id" class="col-md-4 col-lg-3">
                <div class="card h-100">
                    <!-- Image Carousel -->
                    <div v-if="trek.images && trek.images.filter(img => img.startsWith('data:')).length > 0">
                        <div :id="'carousel-' + trek.trek_id" class="carousel slide" data-bs-ride="carousel">
                            <div class="carousel-inner">
                                <div
                                    v-for="(img, index) in trek.images.filter(img => img.startsWith('data:'))"
                                    :key="index"
                                    :class="['carousel-item', index === 0 ? 'active' : '']"
                                >
                                    <img :src="img" class="d-block w-100" style="height: 180px; object-fit: cover;">
                                </div>
                            </div>
                            <template v-if="trek.images.filter(img => img.startsWith('data:')).length > 1">
                                <button class="carousel-control-prev" type="button" :data-bs-target="'#carousel-' + trek.trek_id" data-bs-slide="prev">
                                    <span class="carousel-control-prev-icon"></span>
                                </button>
                                <button class="carousel-control-next" type="button" :data-bs-target="'#carousel-' + trek.trek_id" data-bs-slide="next">
                                    <span class="carousel-control-next-icon"></span>
                                </button>
                            </template>
                        </div>
                    </div>

                    <!-- Fallback -->
                    <img v-else :src="TrekDefault" class="card-img-top" style="height: 180px; object-fit: cover;">

                    <div class="card-body">
                        <h5 class="card-title">{{ trek.trek_name }}</h5>
                        <p class="card-text">
                            <strong>Location:</strong> {{ trek.location }}<br>
                            <strong>Difficulty:</strong> {{ trek.difficulty }}<br>
                            <strong>Duration:</strong> {{ trek.duration_days }} days<br>
                            <strong>Available Slots:</strong> {{ trek.available_slots }}<br>
                            <strong>Price:</strong> ₹{{ trek.price }}/person<br>
                            <strong>Status:</strong> {{ trek.status }}<br>
                        </p>
                        <div class="d-flex gap-2">
                            <button
                                class="btn btn-sm text-white"
                                @click="handleManageClick(trek)"
                                data-bs-toggle="modal"
                                data-bs-target="#staffTrekModal"
                                style="background-color: #9e52eb;"
                            >Manage</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-else class="alert alert-info mt-3">
            No treks are currently assigned to you.
        </div>
    </div>

    <!-- Manage Trek Modal -->
    <div class="modal fade" id="staffTrekModal" tabindex="-1" aria-labelledby="staffTrekModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="staffTrekModalLabel">Manage Trek</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" v-if="currentTrek">
                    <h5>{{ currentTrek.trek_name }}</h5>
                    <p class="text-muted">
                        {{ currentTrek.location }} &middot; {{ currentTrek.difficulty }} &middot; {{ currentTrek.duration_days }} days
                    </p>

                    <div class="mb-3">
                        <label class="form-label">Available Slots</label>
                        <input type="number" min="0" class="form-control" v-model.number="manageForm.available_slots">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Status</label>
                        <select
                            class="form-select"
                            v-model="manageForm.status"
                            :disabled="!canEditStatus"
                        >
                            <option value="Open">Open</option>
                            <option value="Closed">Closed</option>
                        </select>
                        <small class="text-muted" v-if="!canEditStatus">
                            This trek is {{ currentTrek.status }} and can no longer be toggled Open/Closed.
                        </small>
                    </div>
                </div>
                <div class="modal-footer" v-if="currentTrek">
                    <button
                        class="btn btn-success"
                        @click="handleMarkComplete"
                        :disabled="!canEditStatus"
                        style="background-color: #28a745;"
                    >Mark Completed</button>
                    <button class="btn btn-secondary" data-bs-dismiss="modal" style="background-color: #818285;">Close</button>
                    <button class="btn btn-primary text-white" @click="handleSaveChanges" style="background-color: #9e52eb;" :disabled="!canEditStatus">Save Changes</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import TrekDefault from '../../assets/TrekDefault.png'

export default {
    name: 'StaffDashboard',
    data() {
        return {
            TrekDefault,
            treks: [],
            searchQuery: '',
            searchField: 'trek_name',
            sortBy: '',
            filterDifficulty: '',
            filterStatus: '',
            currentTrek: null,
            manageForm: {
                available_slots: 0,
                status: 'Open'
            }
        }
    },
    computed: {
        canEditStatus() {
            return this.currentTrek && ['Approved', 'Open', 'Closed'].includes(this.currentTrek.status)
        },
        filteredTreks() {
            let result = this.treks

            if (this.searchQuery) {
                result = result.filter(trek => {
                    const val = trek[this.searchField]
                    if (val === null || val === undefined) return false
                    return val.toString().toLowerCase().includes(this.searchQuery.toLowerCase())
                })
            }

            if (this.filterDifficulty) {
                result = result.filter(trek => trek.difficulty === this.filterDifficulty)
            }
            if (this.filterStatus) {
                result = result.filter(trek => trek.status === this.filterStatus)
            }

            if (this.sortBy === 'price_asc') result = [...result].sort((a, b) => a.price - b.price)
            else if (this.sortBy === 'price_desc') result = [...result].sort((a, b) => b.price - a.price)
            else if (this.sortBy === 'duration') result = [...result].sort((a, b) => a.duration_days - b.duration_days)

            return result
        }
    },
    methods: {
        async fetchAssignedTreks() {
            try {
                const token = localStorage.getItem('token')
                const response = await axios.get('http://127.0.0.1:5000/staff/treks', {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                this.treks = response.data
            } catch (error) {
                console.error('Error fetching assigned treks:', error)
            }
        },
        handleManageClick(trek) {
            this.currentTrek = trek
            this.manageForm.available_slots = trek.available_slots
            this.manageForm.status = ['Open', 'Closed'].includes(trek.status) ? trek.status : 'Open'
        },
        async handleSaveChanges() {
            try {
                const token = localStorage.getItem('token')
                const payload = { available_slots: this.manageForm.available_slots }
                if (this.canEditStatus) payload.status = this.manageForm.status

                const response = await axios.put(
                    `http://127.0.0.1:5000/treks/${this.currentTrek.trek_id}/staff`,
                    payload,
                    { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } }
                )
                alert(response.data.msg)
                await this.fetchAssignedTreks()
                this.closeModal()
            } catch (error) {
                console.error('Error updating trek:', error)
                alert(error.response?.data?.msg || 'Failed to update trek')
            }
        },
        async handleMarkComplete() {
            if (!confirm('Mark this trek as completed? This will also mark all active bookings as completed.')) return
            try {
                const token = localStorage.getItem('token')
                const response = await axios.put(
                    `http://127.0.0.1:5000/treks/${this.currentTrek.trek_id}/staff`,
                    { complete: true },
                    { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } }
                )
                alert(response.data.msg)
                await this.fetchAssignedTreks()
                this.closeModal()
            } catch (error) {
                console.error('Error completing trek:', error)
                alert(error.response?.data?.msg || 'Failed to mark trek as completed')
            }
        },
        closeModal() {
            const modalEl = document.getElementById('staffTrekModal')
            const modal = bootstrap.Modal.getInstance(modalEl)
            if (modal) modal.hide()
            this.currentTrek = null
        },
        resetFilters() {
            this.searchQuery = ''
            this.searchField = 'trek_name'
            this.sortBy = ''
            this.filterDifficulty = ''
            this.filterStatus = ''
        }
    },
    mounted() {
        this.fetchAssignedTreks()
    }
}
</script>

<style scoped>
.btn {
    opacity: 1 !important;
}
</style>