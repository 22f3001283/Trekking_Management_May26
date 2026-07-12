<template>
  <div>
    <UserNavbar />

    <div class="container" style="padding-top: 90px; padding-bottom: 60px;">
      <div class="row justify-content-center">
        <div class="col-lg-7 col-md-9">

          <!-- Loading state -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <!-- Error state -->
          <div v-else-if="loadError" class="alert alert-danger mt-4" role="alert">
            {{ loadError }}
          </div>

          <!-- Profile card -->
          <div v-else class="card border-0 shadow-sm">
            <div class="card-header d-flex align-items-center gap-3 py-4 px-4" style="background-color: lightblue;">
              <div class="rounded-circle bg-white d-flex align-items-center justify-content-center fw-semibold flex-shrink-0"
                   style="width: 56px; height: 56px; font-size: 1.1rem;">
                {{ initials }}
              </div>
              <div class="flex-grow-1">
                <h4 class="mb-1">{{ profile.username }}</h4>
                <span class="badge text-uppercase" style="font-size: 0.7rem; letter-spacing: 0.05em;">
                  {{ profile.role }}
                </span>
              </div>
              <button class="btn btn-light btn-sm flex-shrink-0" @click="openEditModal">
                <i class="bi bi-pencil-square me-1"></i> Edit
              </button>
            </div>

            <div class="card-body p-4">
              <form>
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label text-muted small text-uppercase" style="letter-spacing: 0.04em;">Username</label>
                    <input type="text" class="form-control" :value="profile.username" disabled>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted small text-uppercase" style="letter-spacing: 0.04em;">Email</label>
                    <input type="text" class="form-control" :value="profile.email" disabled>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted small text-uppercase" style="letter-spacing: 0.04em;">Contact</label>
                    <input type="text" class="form-control" :value="profile.contact || '—'" disabled>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted small text-uppercase" style="letter-spacing: 0.04em;">Role</label>
                    <input type="text" class="form-control text-capitalize" :value="profile.role" disabled>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label text-muted small text-uppercase" style="letter-spacing: 0.04em;">Status</label>
                    <input type="text" class="form-control text-capitalize fw-semibold" :class="statusClass" :value="profile.status" disabled>
                  </div>
                  <div class="col-md-6" v-if="profile.created_at">
                    <label class="form-label text-muted small text-uppercase" style="letter-spacing: 0.04em;">Member Since</label>
                    <input type="text" class="form-control" :value="formattedDate" disabled>
                  </div>
                </div>
              </form>
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
        <div class="modal-content">
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
                  class="form-control"
                  v-model.trim="form.username"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Email</label>
                <input
                  type="email"
                  class="form-control"
                  v-model.trim="form.email"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Contact</label>
                <input
                  type="text"
                  class="form-control"
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
                  class="form-control"
                  v-model="form.current_password"
                  autocomplete="current-password"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">New Password</label>
                <input
                  type="password"
                  class="form-control"
                  v-model="form.new_password"
                  autocomplete="new-password"
                />
              </div>

            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
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
      if (s === 'active') return 'text-success'
      if (s === 'blacklisted') return 'text-danger'
      return 'text-body'
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