<template>
  <nav class="navbar navbar-light bg-light fixed-top">
    <div class="container-fluid">
      <div class="d-flex align-items-center gap-2">
        <button class="hamburger-btn" type="button" data-bs-toggle="offcanvas" data-bs-target="#adminSidebarMenu" aria-controls="adminSidebarMenu">
          <span></span>
          <span></span>
          <span></span>
        </button>
        <a class="navbar-brand mb-0" href="#">TrekAdmin</a>
      </div>

      <div class="d-flex gap-3 align-items-center">
        <span class="page-label d-none d-sm-inline">{{ currentPageLabel }}</span>
        <div class="icon-wrap">
          <button class="icon-btn" @click="signOut">
            <img src="../assets/signout.png" alt="Sign Out" class="nav-icon" />
          </button>
          <span class="tooltip-label">Sign Out</span>
        </div>
      </div>
    </div>
  </nav>

  <!-- Sidebar Menu -->
  <div class="offcanvas offcanvas-start" tabindex="-1" id="adminSidebarMenu" aria-labelledby="adminSidebarMenuLabel">
    <div class="offcanvas-header">
      <h5 class="offcanvas-title" id="adminSidebarMenuLabel">TrekAdmin</h5>
      <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body d-flex flex-column p-0">
      <button
        v-for="item in navItems"
        :key="item.path"
        class="sidebar-link"
        :class="{ 'sidebar-link-active': $route.path === item.path }"
        data-bs-dismiss="offcanvas"
        @click="navigate(item.path)"
      >
        {{ item.label }}
      </button>
      <button class="sidebar-link sidebar-link-danger" data-bs-dismiss="offcanvas" @click="signOut">Sign Out</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminNavbar',
  data() {
    return {
      navItems: [
        { path: '/admin', label: 'Dashboard' },
        { path: '/admin/treks', label: 'Treks' },
        { path: '/admin/staff', label: 'Staff' },
        { path: '/bookings', label: 'Bookings' },
        { path: '/admin/users', label: 'Users' },
        { path: '/admin/stats', label: 'Statistics' }
      ]
    }
  },
  computed: {
    currentPageLabel() {
      const match = this.navItems.find(i => i.path === this.$route.path)
      return match ? match.label : 'Admin'
    }
  },
  methods: {
    navigate(path) {
      this.$router.push(path)
    },
    signOut() {
      if (!confirm('Are you sure you want to sign out?')) return
      localStorage.removeItem('token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('role')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.hamburger-btn {
  background: none;
  border: none;
  padding: 6px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.15s ease;
}

.hamburger-btn:hover {
  background-color: rgba(0, 0, 0, 0.08);
}

.hamburger-btn span {
  display: block;
  width: 22px;
  height: 2px;
  background-color: #333;
  border-radius: 1px;
}

.page-label {
  font-size: 0.85rem;
  color: #5a6472;
}

.icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease;
}

.icon-btn:hover {
  background-color: rgba(0, 0, 0, 0.08);
}

.icon-btn:active {
  background-color: rgba(0, 0, 0, 0.14);
}

.nav-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.tooltip-label {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background-color: #333;
  color: #fff;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s ease;
  z-index: 9999;
}

.tooltip-label::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-bottom-color: #333;
}

.icon-wrap:hover .tooltip-label {
  opacity: 1;
}

.sidebar-link {
  background: none;
  border: none;
  text-align: left;
  padding: 14px 20px;
  font-size: 0.95rem;
  color: #1b2430;
  border-bottom: 1px solid #eceef2;
  transition: background-color 0.15s ease;
}

.sidebar-link:hover {
  background-color: #eef1fc;
  color: #4169e1;
}

.sidebar-link-active {
  background-color: #eef1fc;
  color: #4169e1;
  font-weight: 600;
}

.sidebar-link-danger:hover {
  background-color: #fdecec;
  color: #b91c1c;
}
</style>