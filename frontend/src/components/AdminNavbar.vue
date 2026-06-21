<template>
    <nav class="navbar fixed-top px-4" style="background-color: #fff; border-bottom: 2px solid #f3edff; height: 56px;">
        <div class="container-fluid p-0 d-flex align-items-center gap-3">

            <!-- Toggler on the LEFT -->
            <button class="navbar-toggler border-0 p-1" type="button"
                data-bs-toggle="offcanvas" data-bs-target="#adminOffcanvas"
                aria-controls="adminOffcanvas" aria-label="Toggle navigation"
                style="color: #9e52eb;">
                <span class="navbar-toggler-icon" style="filter: invert(35%) sepia(80%) saturate(600%) hue-rotate(240deg);"></span>
            </button>

            <!-- Brand -->
            <a class="navbar-brand fw-bold p-0 mb-0" style="color: #9e52eb; font-size: 1.1rem; letter-spacing: -0.01em;">
                🏔️ TrekAdmin
            </a>

            <!-- Right side: current page label + sign out -->
            <div class="d-flex align-items-center gap-2 ms-auto">
                <span class="badge rounded-pill px-3 py-2" style="background-color: #f3edff; color: #7c3fc2; font-size: 0.75rem;">
                    {{ currentPageLabel }}
                </span>
                <button class="btn btn-sm rounded-pill px-3" style="background-color: #fee2e2; color: #b91c1c; border: none;" @click="signOut">
                    Sign Out
                </button>
            </div>
        </div>
    </nav>

    <!-- Offcanvas -->
    <div class="offcanvas offcanvas-start" tabindex="-1" id="adminOffcanvas" aria-labelledby="adminOffcanvasLabel"
        style="width: 260px; border-right: 2px solid #f3edff;">
        <div class="offcanvas-header pb-2" style="background-color: #f3edff;">
            <div>
                <h6 class="offcanvas-title fw-bold mb-0" id="adminOffcanvasLabel" style="color: #7c3fc2;">🏔️ TrekAdmin</h6>
                <span class="text-muted" style="font-size: 0.7rem;">Admin Panel</span>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
        </div>
        <div class="offcanvas-body px-3 pt-3">
            <p class="text-uppercase text-muted mb-2" style="font-size: 0.65rem; letter-spacing: .1em;">Navigation</p>
            <ul class="navbar-nav flex-column gap-1">
                <li v-for="item in navItems" :key="item.path" class="nav-item">
                    <a class="nav-link d-flex align-items-center gap-2 rounded-2 px-3 py-2"
                        :class="{ 'active-nav-link': $route.path === item.path }"
                        style="cursor: pointer; font-size: 0.9rem;"
                        @click="navigate(item.path)"
                        data-bs-dismiss="offcanvas">
                        <span>{{ item.icon }}</span>
                        <span>{{ item.label }}</span>
                    </a>
                </li>
            </ul>

            <hr style="border-color: #f3edff;">

            <button class="btn w-100 rounded-pill py-2 mt-1"
                style="background-color: #fee2e2; color: #b91c1c; border: none; font-size: 0.85rem;"
                @click="signOut">
                🚪 Sign Out
            </button>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AdminNavbar',
    data() {
        return {
            navItems: [
                { path: '/admin',         icon: '📊', label: 'Dashboard'  },
                { path: '/admin/treks',   icon: '🏔️', label: 'Treks'      },
                { path: '/admin/staff',   icon: '🧑‍✈️', label: 'Staff'      },
                { path: '/bookings',      icon: '🎒', label: 'Bookings'   },
                { path: '/admin/users',   icon: '🧑‍🤝‍🧑', label: 'Users'      },
            ]
        }
    },
    computed: {
        currentPageLabel() {
            const match = this.navItems.find(i => i.path === this.$route.path)
            return match ? match.icon + ' ' + match.label : 'Admin'
        }
    },
    methods: {
        navigate(path) {
            this.$router.push(path)
        },
        signOut() {
            localStorage.removeItem('token')
            localStorage.removeItem('user_id')
            localStorage.removeItem('role')
            this.$router.push('/login')
        }
    }
}
</script>

<style scoped>
.active-nav-link {
    background-color: #f3edff;
    color: #7c3fc2 !important;
    font-weight: 600;
}
.nav-link {
    color: #444;
    transition: background-color 0.15s;
}
.nav-link:hover {
    background-color: #f9f6ff;
    color: #9e52eb;
}
</style>