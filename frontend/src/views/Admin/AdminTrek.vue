<template>
    
    <AdminNavbar />
    <div class="container-fluid" style="margin-top: 70px;">
        <div class="d-flex justify-content-center mb-3">
            <button class="btn text-white" style="background-color: #9e52eb; margin-top: 10px;" @click="handleCreateClick" data-bs-toggle="modal" data-bs-target="#trekModal">+ Create New Trek</button>
        </div>
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
                    <option value="price">Price</option>
                    <option value="average_rating">Rating</option>
                    <option value="available_slots">Available Slots</option>
                    <option value="assigned_staff_name">Guide</option>
                </select>
            </div>

            <!-- Sort Dropdown -->
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
                        <option value="rating">Rating</option>
                    </select>
                </div>
            </div>

            <!-- Filter Dropdown -->
            <div class="dropdown">
                <button class="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                    Filter
                </button>
                <div class="dropdown-menu p-3" style="min-width: 280px;">

                    <!-- Difficulty -->
                    <label class="form-label fw-bold">Difficulty</label>
                    <select class="form-select mb-3" v-model="filterDifficulty">
                        <option value="">All</option>
                        <option value="Easy">Easy</option>
                        <option value="Moderate">Moderate</option>
                        <option value="Hard">Hard</option>
                    </select>

                    <!-- Status -->
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

                    <!-- Price Range -->
                    <label class="form-label fw-bold">Price Range</label>
                    <div class="d-flex gap-2 mb-3">
                        <input class="form-control" type="number" v-model="filterMinPrice" placeholder="Min">
                        <input class="form-control" type="number" v-model="filterMaxPrice" placeholder="Max">
                    </div>

                    <button class="btn btn-outline-danger w-100" @click="resetFilters">Reset Filters</button>
                </div>
            </div>

        </div>
    </div>

    <!-- Trek Cards -->
    <div id="trekPanel" style="padding-left: 100px; padding-right: 100px;">
        <h2>All Treks</h2>
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
                            <strong>Duration:</strong> {{ trek.duration_days }} days<br>
                            <strong>Guide:</strong> {{ trek.assigned_staff_name || 'Not assigned' }}<br>
                            <strong>Available Slots:</strong> {{ trek.available_slots }}<br>
                            <strong>Price:</strong> ₹{{ trek.price }}/person<br>
                            <strong>Status:</strong> {{ trek.status }}<br>
                            <strong>Rating:</strong> {{ trek.average_rating ? trek.average_rating + '/5' : 'No ratings' }}
                        </p>
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm text-white" @click="handleViewClick(trek)" data-bs-toggle="modal" data-bs-target="#trekModal" style="background-color: #9e52eb;">View</button>
                            <button class="btn btn-sm btn-warning" @click="handleEditClick(trek)" data-bs-toggle="modal" data-bs-target="#trekModal" style="background-color: #ffdd00;">Edit</button>
                            <button class="btn btn-sm btn-danger" @click="handleDeleteTrek(trek.trek_id)" style="background-color: #d63a3a;">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-else class="alert alert-info mt-3">
            No treks available. <a href="#" @click="handleCreateClick" data-bs-toggle="modal" data-bs-target="#trekModal">Create one now</a>
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
            else if (this.sortBy === 'rating') result = [...result].sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0))

            return result
        }
    },
    methods: {
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
                    const modal = bootstrap.Modal.getInstance(document.getElementById('trekModal'))
                    modal.hide()
                }
            } catch (error) {
                console.error('Error submitting trek form:', error)
                alert(error.response?.data?.msg || 'Failed to save trek')
            }
        },
        async handleDeleteTrek(trek_id) {
            if (!confirm('Are you sure you want to delete this trek?')) return
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
    .btn {
    opacity: 1 !important;
    }
</style>