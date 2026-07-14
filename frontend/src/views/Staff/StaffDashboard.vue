<template>
    <StaffNavbar />

    <div class="container-fluid responsive-container" style="padding-top: 80px;">
        <h2 style="padding-bottom: 5px;">My Dashboard</h2>
        <!-- KPI Summary -->
        <div class="row g-3 mb-4">
            <div class="col-6 col-lg-4">
                <div class="card h-100 border-1 shadow-sm kpi-card">
                    <div class="card-body">
                        <div class="text-muted text-uppercase kpi-label">Assigned Treks</div>
                        <div class="kpi-value">{{ assignedTreksCount }}</div>
                    </div>
                </div>
            </div>
            <div class="col-6 col-lg-4">
                <div class="card h-100 border-1 shadow-sm kpi-card">
                    <div class="card-body">
                        <div class="text-muted text-uppercase kpi-label">Total Participants</div>
                        <div class="kpi-value">{{ totalParticipants }}</div>
                    </div>
                </div>
            </div>
            <div class="col-12 col-lg-4">
                <div class="card h-100 border-1 shadow-sm kpi-card">
                    <div class="card-body">
                        <div class="text-muted text-uppercase kpi-label">Ongoing Tasks</div>
                        <div class="kpi-value">{{ ongoingTasksCount }}</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-center gap-3 mb-4">

            <h3 style="padding-bottom: 5px;">My Assigned Treks</h3>

            <div class="d-flex flex-column flex-lg-row justify-content-lg-end align-items-lg-center gap-2 mb-3">

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
                    <button class="btn btn-light dropdown-toggle" type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                        <i class="bi bi-sort-alpha-down"></i> Sort
                    </button>
                    <div class="dropdown-menu p-3" style="min-width: 220px;">
                        <label class="form-label fw-bold">Sort By</label>
                        <select class="form-select" v-model="sortBy">
                            <option value="">None</option>
                            <option value="price_asc">Price: Low to High</option>
                            <option value="price_desc">Price: High to Low</option>
                            <option value="duration">No. of Days</option>
                        </select>
                    </div>
                </div>

                <!-- Filter -->
                <div class="dropdown">
                    <button class="btn btn-light dropdown-toggle" type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                        <i class="bi bi-funnel"></i> Filter
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
    </div>

    <!-- Trek Cards -->
    <div id="trekPanel" class="responsive-container">
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
                            <strong>Dates:</strong> {{ formatDate(trek.start_date) }} - {{ formatDate(trek.end_date) }} ({{ trek.duration_days }} days)<br>
                            <strong>Available Slots:</strong> {{ trek.available_slots }}<br>
                            <strong>Price:</strong> ₹{{ trek.price }}/person<br>
                            <strong>Status:</strong> {{ trek.status }}<br>
                        </p>
                        <div class="d-flex gap-2 flex-column flex-sm-row">
                            <button
                                class="btn btn-sm btn-primary"
                                @click="handleManageClick(trek)"
                                data-bs-toggle="modal"
                                data-bs-target="#staffTrekModal"
                            >Manage</button>
                            <button
                                class="btn btn-sm btn-outline-primary"
                                @click="handleViewBookings(trek)"
                            >View Bookings</button>                            
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
                        <small class="text-muted">
                            {{ currentTrek.booked_count || 0 }} participant(s) already booked on this trek.
                        </small>
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
                    <button class="btn btn-mark-complete" @click="handleMarkComplete" :disabled="!canEditStatus">Mark Completed</button>
                    <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button class="btn btn-save-changes" @click="handleSaveChanges" :disabled="!canEditStatus">Save Changes</button>
                </div>
            </div>
        </div>
    </div>
    <footer class="bg-light text-center py-3 small" style="margin-top: 20px">
        © 2026 Trekking Management. All rights reserved.
    </footer> 
</template>

<script>
import axios from 'axios'
import TrekDefault from '../../assets/TrekDefault.png'
import StaffNavbar from '../../components/StaffNavbar.vue'

export default {
    name: 'StaffDashboard',
    components: {
        StaffNavbar
    },
    data() {
        return {
            TrekDefault,
            treks: [],
            bookings: [],
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
        assignedTreksCount() {
            return this.treks.length
        },
        ongoingTasksCount() {
            return this.treks.filter(t => ['Open', 'Closed'].includes(t.status)).length
        },
        totalParticipants() {
            return this.bookings
                .filter(b => b.status === 'Booked')
                .reduce((sum, b) => sum + (b.num_people || 0), 0)
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
        formatDate(date) {
            if (!date) return '';

            return new Date(date).toLocaleDateString('en-IN', {
                day: 'numeric',
                month: 'short',
                year: 'numeric'
            });
        },
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
        async fetchBookings() {
            try {
                const token = localStorage.getItem('token')
                const response = await axios.get('http://127.0.0.1:5000/bookings', {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                this.bookings = response.data
            } catch (error) {
                console.error('Error fetching bookings:', error)
                this.bookings = []
            }
        },
        handleManageClick(trek) {
            this.currentTrek = trek
            this.manageForm.available_slots = trek.available_slots
            this.manageForm.status = ['Open', 'Closed'].includes(trek.status) ? trek.status : 'Open'
        },
        handleViewBookings(trek) {
            this.$router.push({ path: '/bookings', query: { trek_id: trek.trek_id } })
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
                await this.fetchBookings()
                this.closeModal()
            } catch (error) {
                console.error('Error completing trek:', error)
                alert(error.response?.data?.msg || 'Failed to mark trek as completed')
            }
        },
        closeModal() {
            const modalEl = document.getElementById('staffTrekModal')
            const modal = bootstrap.Modal.getInstance(modalEl)
            document.activeElement?.blur()
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
        this.fetchBookings()
    }
}
</script>

<style scoped>
h2,h3 {
    font-weight: 600;
    color: #1b2430;
    letter-spacing: -0.01em;
    border-bottom: 2px solid #4169e1;
    display: inline-block;
}

.btn-mark-complete {
    color: #fff;
    background-color: #198754;
    border-color: #198754;
}

.btn-mark-complete:hover:not(:disabled) {
    background-color: #157347;
    border-color: #157347;
    color: #fff;
}

.btn-mark-complete:disabled {
    color: #6b7280;
    background-color: transparent;
    border-color: #198754;
    opacity: 1;
}

.btn-save-changes {
    color: #fff;
    background-color: #4169e1;
    border-color: #4169e1;
}

.btn-save-changes:hover:not(:disabled) {
    background-color: #3457c4;
    border-color: #3457c4;
    color: #fff;
}

.btn-save-changes:disabled {
    color: #6b7280;
    background-color: transparent;
    border-color: #4169e1;
    opacity: 1;
}

.card {
    border: 1px solid #dfe3ea;
    border-radius: 8px;
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
.card:hover {
    border-color: #c7d1f2;
    box-shadow: 0 4px 14px rgba(23, 43, 99, 0.08);
}

.card-title {
    font-weight: 600;
    color: #1b2430;
}

.card-text {
    color: #4b5563;
    font-size: 0.92rem;
}

.dropdown-menu {
    border: 1px solid #dfe3ea;
    box-shadow: 0 6px 18px rgba(23, 43, 99, 0.1);
}

.form-select:focus,
.form-control:focus {
    border-color: #4169e1;
    box-shadow: 0 0 0 0.2rem rgba(65, 105, 225, 0.15);
}

.alert-info {
    background-color: #eef1fc;
    border-color: #d9e0f7;
    color: #33415e;
}

.kpi-card {
    border: 1px solid #dfe3ea;
}

.kpi-label {
    font-size: 0.72rem;
    letter-spacing: 0.05em;
    font-weight: 600;
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1b2430;
}

.responsive-container {
    padding-left: 20px;
    padding-right: 20px;
}

@media (min-width: 992px) {
    .responsive-container {
        padding-left: 100px;
        padding-right: 100px;
    }
}
</style>