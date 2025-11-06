// firebase-messaging-sw.js
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyC8EiT8cu9Y8D8hbUzZYo56o4kZv7KRD3k",
    authDomain: "mindful-dfeab.firebaseapp.com",
    projectId: "mindful-dfeab",
    storageBucket: "mindful-dfeab.firebasestorage.app",
    messagingSenderId: "271121060617",
    appId: "1:271121060617:web:f94c8fff9d6954714d39d8",
    measurementId: "G-N3SMDQ5JNM"
};

// Initialize Firebase in service worker
firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
    console.log('Received background message:', payload);

    const notificationTitle = payload.notification.title || 'New Message';
    const notificationOptions = {
        body: payload.notification.body || 'You have a new notification',
        icon: '/firebase-logo.png',
        badge: '/badge-icon.png',
        data: payload.data
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    event.notification.close();

    // Open the app when notification is clicked
    event.waitUntil(
        clients.openWindow('/')
    );
});
