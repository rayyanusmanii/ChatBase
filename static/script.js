

const overlay = document.getElementById('modal-overlay');
const picker = document.getElementById('picker');
const modalGroup = document.getElementById('modal-group');
const modalDm = document.getElementById('modal-dm');
const roomInput = document.getElementById('room-name-input');

function showPicker() {
  overlay.style.display = 'flex';
  picker.style.display = 'flex';
  if (modalGroup) modalGroup.style.display = 'none';
  if (modalDm) modalDm.style.display = 'none';
}

function closeModal() {
  overlay.style.display = 'none';
  if (picker) picker.style.display = 'flex';
  if (modalGroup) modalGroup.style.display = 'none';
  if (modalDm) modalDm.style.display = 'none';
  if (roomInput) roomInput.value = '';
  const dmInput = document.getElementById('dm-username-input');
  if (dmInput) dmInput.value = '';
}

document.querySelectorAll('.open-chat').forEach(button => {
  button.addEventListener('click', showPicker);
});

// picker side clicks
const pickGroup = document.getElementById('pick-group');
const pickDm = document.getElementById('pick-dm');

if (pickGroup) {
  pickGroup.addEventListener('click', function() {
    picker.style.display = 'none';
    modalGroup.style.display = 'flex';
    if (roomInput) roomInput.focus();
  });
}

if (pickDm) {
  pickDm.addEventListener('click', function() {
    picker.style.display = 'none';
    modalDm.style.display = 'flex';
    const dmInput = document.getElementById('dm-username-input');
    if (dmInput) dmInput.focus();
  });
}

// close and back buttons
if (document.getElementById('modal-close')) {
  document.getElementById('modal-close').addEventListener('click', closeModal);
}
if (document.getElementById('modal-close-group')) {
  document.getElementById('modal-close-group').addEventListener('click', closeModal);
}
if (document.getElementById('modal-close-dm')) {
  document.getElementById('modal-close-dm').addEventListener('click', closeModal);
}
if (document.getElementById('modal-back-group')) {
  document.getElementById('modal-back-group').addEventListener('click', showPicker);
}
if (document.getElementById('modal-back-dm')) {
  document.getElementById('modal-back-dm').addEventListener('click', showPicker);
}

const modalDmEl = document.getElementById('modal-dm');
if (modalDmEl) {
  modalDmEl.querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('dm-username-input').value.trim();
    if (username) window.location.href = '/dm/' + username;
  });
}

overlay.addEventListener('click', function(e) {
  if (e.target === overlay) closeModal();
});

// add member modal
const memberOverlay = document.getElementById('member-overlay');
const memberInput = document.getElementById('member-username-input');
const addMemberBtn = document.querySelector('.btn-add-member');

if (addMemberBtn) {
  addMemberBtn.addEventListener('click', function() {
    memberOverlay.style.display = 'flex';
    memberInput.focus();
  });
}

function closeMemberModal() {
  memberOverlay.style.display = 'none';
  memberInput.value = '';
}

if (document.getElementById('member-modal-close')) {
  document.getElementById('member-modal-close').addEventListener('click', closeMemberModal);
  document.getElementById('member-modal-cancel').addEventListener('click', closeMemberModal);
  memberOverlay.addEventListener('click', function(e) {
    if (e.target === memberOverlay) closeMemberModal();
  });
}

// view members modal
const membersOverlay = document.getElementById('members-overlay');
const viewMembersBtn = document.querySelector('.btn-view-members');

if (viewMembersBtn) {
  viewMembersBtn.addEventListener('click', function() {
    membersOverlay.style.display = 'flex';
  });
}

function closeMembersModal() {
  membersOverlay.style.display = 'none';
}

if (document.getElementById('members-modal-close')) {
  document.getElementById('members-modal-close').addEventListener('click', closeMembersModal);
  membersOverlay.addEventListener('click', function(e) {
    if (e.target === membersOverlay) closeMembersModal();
  });
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    closeModal();
    if (memberOverlay) closeMemberModal();
    if (membersOverlay) closeMembersModal();
  }
});

// room-specific logic
const msgs = document.getElementById('messages');
if (msgs) {
  var socket = io();
  const roomId = parseInt(msgs.dataset.roomId);

  msgs.scrollTop = msgs.scrollHeight;

  socket.emit('join', { room_id: roomId, username: CURRENT_USER });

  const form = document.querySelector('.input-bar form');
  const input = document.querySelector('.input-wrap input');

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    const content = input.value.trim();
    if (!content) return;
    socket.emit('message', { room_id: roomId, message: content, username: CURRENT_USER });
    input.value = '';
    input.focus();
  });

  socket.on('message', function(data) {
    const empty = msgs.querySelector('.empty-chat');
    if (empty) empty.remove();

    const displayName = data.username === CURRENT_USER ? 'Me' : data.username;
    const div = document.createElement('div');
    div.className = 'message';
    div.innerHTML = `
      <div class="msg-avatar">${displayName[0].toUpperCase()}</div>
      <div class="msg-body">
        <div class="msg-meta">
          <span class="msg-author">${displayName}</span>

        </div>
        <div class="msg-text">${data.content}</div>
      </div>
    `;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  });

  document.querySelector('.input-wrap input').focus();
}
