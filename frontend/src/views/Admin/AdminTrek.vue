<template>
    
    <AdminNavbar />
    <div class="container-fluid" style="margin-top: 70px;">
        <div class="d-flex justify-content-center mb-3">
            <button class="btn btn-outline-primary" style="margin-top: 10px;" @click="handleCreateClick" data-bs-toggle="modal" data-bs-target="#trekModal">+ Create New Trek</button>
        </div>
    </div>

    <div class="container-fluid responsive-container">

        <div class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-center gap-3 mb-4">

            <!-- Left -->
            <h2 class="mb-0">All Treks</h2>

            <!-- Right -->
            <div class="d-flex flex-column flex-sm-row gap-2">

                <!-- Search -->
                <div class="input-group" style="max-width: 370px;">
                    <input
                        class="form-control"
                        type="search"
                        v-model="searchQuery"
                        :placeholder="'Search by ' + searchField.replace('_', ' ') + '...'"
                        aria-label="Search"
                    >
                    <select class="form-select" v-model="searchField" style="max-width: 150px;">
                        <option value="trek_name">Trek Name</option>
                        <option value="location">Location</option>
                        <option value="difficulty">Difficulty</option>
                        <option value="status">Status</option>
                        <option value="price">Price</option>
                        <option value="available_slots">Available Slots</option>
                        <option value="assigned_staff_name">Guide</option>
                    </select>
                </div>

                <!-- Sort Dropdown -->
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
                            <option value="duration">Duration</option>
                        </select>
                    </div>
                </div>

                <!-- Filter Dropdown -->
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
                            <option value="Pending">Pending</option>
                            <option value="Approved">Approved</option>
                            <option value="Open">Open</option>
                            <option value="Closed">Closed</option>
                            <option value="Completed">Completed</option>
                            <option value="Cancelled">Cancelled</option>
                        </select>

                        <label class="form-label fw-bold">Price Range</label>
                        <div class="d-flex flex-column flex-sm-row gap-2">
                            <input class="form-control" type="number" v-model="filterMinPrice" placeholder="Min">
                            <input class="form-control" type="number" v-model="filterMaxPrice" placeholder="Max">
                        </div>

                        <button class="btn btn-outline-danger w-100" style="margin-top:10px" @click="resetFilters">
                            Reset Filters
                        </button>
                    </div>
                </div>

            </div>

        </div>
    

        <!-- Trek Cards -->
        <div id="trekPanel">
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
                                <!-- Only show controls if more than 1 image -->
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

                        <!-- Fallback if no valid images -->
                        <img v-else :src="TrekDefault" class="card-img-top" style="height: 180px; object-fit: cover;">                  
                        <div class="card-body">
                            <h5 class="card-title">{{ trek.trek_name }}</h5>
                            <p class="card-text">
                                <strong>Location:</strong> {{ trek.location }}<br>
                                <strong>Difficulty:</strong> {{ trek.difficulty }}<br>
                                <strong>Dates:</strong> {{ formatDate(trek.start_date) }} - {{ formatDate(trek.end_date) }} ({{ trek.duration_days }} days)<br>
                                <strong>Guide:</strong> {{ trek.assigned_staff_name || 'Not assigned' }}<br>
                                <strong>Available Slots:</strong> {{ trek.available_slots }}<br>
                                <strong>Price:</strong> ₹{{ trek.price }}/person<br>
                                <strong>Status:</strong> {{ trek.status }}<br>
                            </p>
                            <div class="d-flex flex-row flex-wrap gap-2 mb-4">
                                <button class="btn btn-sm btn-outline-primary" @click="handleViewClick(trek)" data-bs-toggle="modal" data-bs-target="#trekModal"><i class="bi bi-eye"></i></button>
                                <button class="btn btn-sm btn-outline-secondary" @click="handleEditClick(trek)" data-bs-toggle="modal" data-bs-target="#trekModal"><i class="bi bi-pencil-square"></i></button>
                                <button class="btn btn-sm btn-outline-danger" @click="handleDeleteTrek(trek.trek_id)"><i class="bi bi-trash3" style="color:crimson;"></i></button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else class="alert alert-info mt-3">
                No treks available. <a href="#" @click="handleCreateClick" data-bs-toggle="modal" data-bs-target="#trekModal">Create one now</a>
            </div>
        </div>  
    </div>

    <!-- Trek Form Modal -->
    <div class="modal fade" id="trekModal" tabindex="-1" aria-labelledby="trekModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="trekModalLabel">{{ currentMode === 'create' ? 'Create Trek' : currentMode === 'edit' ? 'Edit Trek' : 'View Trek' }}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <!-- <Trek :mode="currentMode" :trek="currentTrek" @submit="handleTrekSubmit" @cancel="handleCancel" /> -->
                    <Trek 
                        ref="trekFormRef"
                        :key="currentMode + (currentTrek?.trek_id || 'new')"
                        :mode="currentMode" 
                        :trek="currentTrek" 
                        @submit="handleTrekSubmit" 
                        @cancel="handleCancel" 
                    />
                </div>
            </div>
        </div>
    </div>
    
    <footer class="bg-light text-center py-3 small" style="margin-top: 20px">
        © 2026 Trekking Management. All rights reserved.
    </footer>    
</template>
<script>
import axios from 'axios';
import TrekDefault from '../../assets/TrekDefault.png'
import Trek from '../../components/Trek.vue';
import AdminNavbar from '../../components/AdminNavbar.vue';

export default {
    components: { Trek, AdminNavbar },
    data() {
        return {
            TrekDefault,
            treks: [],
            searchQuery: '',
            currentMode: 'create', // create | edit | view
            currentTrek: null,
            isLoading: false,
            searchField : 'trek_name',
            sortBy: '',
            filterDifficulty: '',
            filterStatus: '',
            filterMinPrice: '',
            filterMaxPrice: '',
        }
    },
    computed: {
        filteredTreks() {
            let result = this.treks

            // Search
            if (this.searchQuery) {
                result = result.filter(trek => {
                    const val = trek[this.searchField]
                    if (val === null || val === undefined) return false
                    return val.toString().toLowerCase().includes(this.searchQuery.toLowerCase())
                })
            }

            // Filter
            if (this.filterDifficulty) {
                result = result.filter(trek => trek.difficulty === this.filterDifficulty)
            }
            if (this.filterStatus) {
                result = result.filter(trek => trek.status === this.filterStatus)
            }
            if (this.filterMinPrice !== '') {
                result = result.filter(trek => trek.price >= parseFloat(this.filterMinPrice))
            }
            if (this.filterMaxPrice !== '') {
                result = result.filter(trek => trek.price <= parseFloat(this.filterMaxPrice))
            }

            // Sort
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
        async fetchTreks() {
            try {
                this.isLoading = true
                const token = localStorage.getItem('token')
                const response = await axios.get('http://127.0.0.1:5000/treks', {
                    headers: { 'Authorization': `Bearer ${token}` },
                })
                this.treks = response.data
            } catch (error) {
                console.error('Error fetching treks:', error)
            } finally {
                this.isLoading = false
            }
        },
        handleCreateClick() {
            this.currentMode = 'create'
            this.currentTrek = null
        },
        handleEditClick(trek) {
            this.currentMode = 'edit'
            this.currentTrek = trek
        },
        handleViewClick(trek) {
            this.currentMode = 'view'
            this.currentTrek = trek
        },
        async handleTrekSubmit(formData) {
            if (!formData || formData.isTrusted !== undefined) {
                console.error('Received event object instead of form data')
                return
            }
            try {
                const token = localStorage.getItem('token')
                if (this.currentMode === 'create') {
                    const response = await axios.post('http://127.0.0.1:5000/treks', formData, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                    })
                    alert(response.data.msg)
                    await this.fetchTreks()
                    this.$refs.trekFormRef.resetForm() 
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('trekModal'))
                    modal.hide()
                } else if (this.currentMode === 'edit') {
                    const response = await axios.put(`http://127.0.0.1:5000/treks/${this.currentTrek.trek_id}`, formData, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                    })
                    alert(response.data.msg)
                    await this.fetchTreks()
                    this.$refs.trekFormRef.resetForm() 
                    const modal = bootstrap.Modal.getInstance(document.getElementById('trekModal'))
                    modal.hide()
                }
            } catch (error) {
                console.error('Error submitting trek form:', error)
                alert(error.response?.data?.msg || 'Failed to save trek')
            }
        },
        async handleDeleteTrek(trek_id) {
            if (!confirm('Are you sure you want to delete this trek? This action is permanent and cannot be undone.')) return
            try {
                const token = localStorage.getItem('token')
                const response = await axios.delete(`http://127.0.0.1:5000/treks/${trek_id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                alert(response.data.msg)
                await this.fetchTreks()
            } catch (error) {
                console.error('Error deleting trek:', error)
                alert(error.response?.data?.msg || 'Failed to delete trek')
            }
        },
        handleCancel() {
            document.activeElement.blur()
            this.$refs.trekFormRef.resetForm() 
            const modal = bootstrap.Modal.getInstance(document.getElementById('trekModal'))
            modal.hide()
        },
        resetFilters() {
            this.searchQuery = ''
            this.searchField = 'trek_name'
            this.sortBy = ''
            this.filterDifficulty = ''
            this.filterStatus = ''
            this.filterMinPrice = ''
            this.filterMaxPrice = ''
        },
    },
    mounted() {
        this.fetchTreks()
    }
}
</script>
<style scoped>

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