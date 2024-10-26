use git2::{Cred, RemoteCallbacks};

pub(crate) fn get_auth_callback() -> RemoteCallbacks<'static> {
  let mut callback = RemoteCallbacks::new();

  // Set up authentication callback for SSH or HTTPS
  callback.credentials(|_url, username_from_url, allowed_types| {
    // Use SSH key authentication
    if allowed_types.contains(git2::CredentialType::SSH_KEY) {
      return Cred::ssh_key(
        username_from_url.unwrap(),
        None,
        std::path::Path::new("~/.ssh/id_rsa"),
        None,
      );

    // Use username/password authentication for HTTPS
    } else if allowed_types.contains(git2::CredentialType::USER_PASS_PLAINTEXT) {
      return Cred::userpass_plaintext("your-username", "your-password");
    } else {
      return Err(git2::Error::from_str(
        "No authentication method available. Please generate a SSH key",
      ));
    }
  });

  return callback;
}
