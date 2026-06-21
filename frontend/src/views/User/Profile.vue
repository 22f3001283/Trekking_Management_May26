<template>
  <div class="profile-page">
    <UserNavbar />

    <div class="container profile-container">
      <div class="row justify-content-center">
        <div class="col-lg-7 col-md-9">

          <!-- Loading state -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-purple" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <!-- Error state -->
          <div v-else-if="loadError" class="alert alert-danger mt-4" role="alert">
            {{ loadError }}
          </div>

          <!-- Profile card -->
          <div v-else class="card profile-card shadow-sm">
            <div class="card-header-purple">
              <div class="avatar-circle">
                {{ initials }}
              </div>
              <div class="header-text">
                <h4 class="mb-0">{{ profile.username }}</h4>
                <span class="role-badge">{{ profile.role }}</span>
              </div>
              <button class="btn btn-edit" @click="openEditModal">
                <i class="bi bi-pencil-square me-1"></i> Edit
              </button>
            </div>

            <div class="card-body">
              <div class="detail-row">
                <span class="detail-label">Username</span>
                <span class="detail-value">{{ profile.username }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Email</span>
                <span class="detail-value">{{ profile.email }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Contact</span>
                <span class="detail-value">{{ profile.contact || '—' }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Role</span>
                <span class="detail-value text-capitalize">{{ profile.role }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Status</span>
                <span class="detail-value">
                  <span :class="['status-pill', statusClass]">{{ profile.status }}</span>
                </span>
              </div>
              <div class="detail-row" v-if="profile.created_at">
                <span class="detail-label">Member Since</span>
                <span class="detail-value">{{ formattedDate }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div
      class="modal fade"
      id="editProfileModal"
      tabindex="-1"
      aria-labelledby="editProfileModalLabel"
      aria-hidden="true"
      ref="editModalEl"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content modal-purple">
          <div class="modal-header">
            <h5 class="modal-title" id="editProfileModalLabel">Edit Profile</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>

          <form @submit.prevent="submitEdit">
            <div class="modal-body">

              <div v-if="editError" class="alert alert-danger py-2">{{ editError }}</div>
              <div v-if="editSuccess" class="alert alert-success py-2">{{ editSuccess }}</div>

              <div class="mb-3">
                <label class="form-label">Username</label>
                <input
                  type="text"
                  class="form-control input-purple"
                  v-model.trim="form.username"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Email</label>
                <input
                  type="email"
                  class="form-control input-purple"
                  v-model.trim="form.email"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Contact</label>
                <input
                  type="text"
                  class="form-control input-purple"
                  v-model.trim="form.contact"
                  placeholder="Phone number"
                />
              </div>

              <hr class="my-3" />
              <p class="text-muted small mb-2">Leave password fields blank to keep your current password.</p>

              <div class="mb-3">
                <label class="form-label">Current Password</label>
                <input
                  type="password"
                  class="form-control input-purple"
                  v-model="form.current_password"
                  autocomplete="current-password"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">New Password</label>
                <input
                  type="password"
                  class="form-control input-purple"
                  v-model="form.new_password"
                  autocomplete="new-password"
                />
              </div>

            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="submit" class="btn btn-save" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                Save Changes
              </button>
            </div>
          </form>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import UserNavbar from '../../components/UserNavbar.vue'

export default {
  name: 'Profile',
  components: { UserNavbar },
  data() {
    return {
      profile: {},
      loading: true,
      loadError: '',
      saving: false,
      editError: '',
      editSuccess: '',
      modalInstance: null,
      form: {
        username: '',
        email: '',
        contact: '',
        current_password: '',
        new_password: ''
      }
    }
  },
  computed: {
    initials() {
      if (!this.profile.username) return '?'
      return this.profile.username.slice(0, 2).toUpperCase()
    },
    statusClass() {
      const s = (this.profile.status || '').toLowerCase()
      if (s === 'active') return 'status-active'
      if (s === 'inactive') return 'status-inactive'
      if (s === 'blacklisted') return 'status-blacklisted'
      return ''
    },
    formattedDate() {
      if (!this.profile.created_at) return ''
      const d = new Date(this.profile.created_at)
      if (isNaN(d)) return this.profile.created_at
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
    }
  },
  mounted() {
    this.fetchProfile()
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem('token')
      return { Authorization: `Bearer ${token}` }
    },
    async fetchProfile() {
      this.loading = true
      this.loadError = ''
      try {
        const res = await axios.get('http://127.0.0.1:5000/user/profile', { headers: this.authHeaders() })
        this.profile = res.data
      } catch (err) {
        this.loadError =
          err.response?.data?.msg || 'Could not load your profile. Please try again.'
      } finally {
        this.loading = false
      }
    },
    openEditModal() {
      this.editError = ''
      this.editSuccess = ''
      this.form = {
        username: this.profile.username || '',
        email: this.profile.email || '',
        contact: this.profile.contact || '',
        current_password: '',
        new_password: ''
      }
      this.modalInstance = bootstrap.Modal.getOrCreateInstance(this.$refs.editModalEl)
      this.modalInstance.show()
    },
    async submitEdit() {
      this.editError = ''
      this.editSuccess = ''

      if (this.form.new_password && !this.form.current_password) {
        this.editError = 'Enter your current password to set a new one.'
        return
      }

      this.saving = true
      try {
        const payload = {
          username: this.form.username,
          email: this.form.email,
          contact: this.form.contact
        }
        if (this.form.new_password) {
          payload.current_password = this.form.current_password
          payload.new_password = this.form.new_password
        }

        const res = await axios.put('http://127.0.0.1:5000/user/profile', payload, { headers: this.authHeaders() })
        this.profile = res.data.user || { ...this.profile, ...payload }
        this.editSuccess = res.data.msg || 'Profile updated successfully'

        // brief pause so the user sees the success message, then close
        setTimeout(() => {
          this.modalInstance.hide()
          this.editSuccess = ''
        }, 900)
      } catch (err) {
        this.editError = err.response?.data?.msg || 'Could not update profile. Please try again.'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.profile-page {
  background-color: #faf7fe;
  min-height: 100vh;
}

.profile-container {
  padding-top: 90px;
  padding-bottom: 60px;
}

.text-purple {
  color: #9e52eb;
}

/* Card */
.profile-card {
  border: none;
  border-radius: 14px;
  overflow: hidden;
}

.card-header-purple {
  background: linear-gradient(135deg, #9e52eb 0%, #7c3fc2 100%);
  color: #fff;
  padding: 28px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-circle {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
}

.header-text {
  flex-grow: 1;
}

.role-badge {
  display: inline-block;
  margin-top: 4px;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background-color: rgba(255, 255, 255, 0.22);
  padding: 2px 10px;
  border-radius: 12px;
}

.btn-edit {
  background-color: #fff;
  color: #7c3fc2;
  border: none;
  font-weight: 500;
  border-radius: 8px;
  padding: 6px 16px;
  flex-shrink: 0;
}

.btn-edit:hover {
  background-color: #f3edff;
  color: #5b2ea0;
}

/* Detail rows */
.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 4px;
  border-bottom: 1px solid #f1eafc;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  color: #8a8a8a;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.detail-value {
  font-weight: 500;
  color: #2d2d2d;
}

/* Status pill */
.status-pill {
  font-size: 0.75rem;
  padding: 3px 12px;
  border-radius: 12px;
  text-transform: capitalize;
  font-weight: 500;
}

.status-active {
  background-color: #e8f8ee;
  color: #1f9d55;
}

.status-inactive {
  background-color: #fdf0e3;
  color: #c4791f;
}

.status-blacklisted {
  background-color: #fde8e8;
  color: #c43030;
}

/* Modal */
.modal-purple .modal-header {
  background-color: #f3edff;
  border-bottom: 1px solid #e6d8fb;
}

.modal-purple .modal-title {
  color: #7c3fc2;
  font-weight: 600;
}

.input-purple:focus {
  border-color: #9e52eb;
  box-shadow: 0 0 0 0.2rem rgba(158, 82, 235, 0.15);
}

.btn-save {
  background-color: #9e52eb;
  border: none;
  color: #fff;
  font-weight: 500;
}

.btn-save:hover {
  background-color: #7c3fc2;
}

.btn-save:disabled {
  background-color: #c9a3ee;
}
</style>