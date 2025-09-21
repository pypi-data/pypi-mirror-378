import os
from rose_sdk import RoseClient
from rose_sdk.exceptions import RoseAPIError, RosePermissionError, RoseConflictError


BASE_URL = "https://admin-test.rose.blendvision.com"


def get_root_client():
    """Initialize RoseClient with admin/root token."""
    root_token = os.getenv("ROSE_ADMIN_TOKEN")
    if not root_token:
        raise RuntimeError(
            "❌ ROSE_ADMIN_TOKEN not set.\n"
            "   Example: export ROSE_ADMIN_TOKEN='your_root_token_here'"
        )
    return RoseClient(base_url=BASE_URL, root_token=root_token)


def create_account(client:RoseClient, account_id: str):
    """Try to create an account. Returns role object."""
    try:
        role = client.accounts.create(account_id)
        print(f"✅ Account created: {role.account_id} (role_id={role.role_id})")
        return role
    except RoseConflictError:
        print(f"⚠️  Account '{account_id}' already exists, skipping creation")
        # Fetch role info if API provides a way (or reuse account_id if sufficient)
        role = client.roles.list()
        print(role)
        return account_id  # Assuming this API exists


def issue_token(client, role_id: str, tenant_id: str):
    """Issue a token for given role."""
    role_with_token = client.roles.issue_token(role_id=role_id, tenant_id=tenant_id)
    print(f"✅ Token issued (expires {role_with_token.expired_at})")
    return role_with_token


def create_account_with_token(account_id="luli"):
    """Orchestrate: create account (if not exists) and issue a token."""
    client = get_root_client()
    try:
        role = create_account(client, account_id)
        token_info = issue_token(client, role.role_id, role.account_id)
        return {
            "account_id": role.account_id,
            "role_id": role.role_id,
            "access_token": token_info.token,
            "expired_at": token_info.expired_at,
        }
    except RosePermissionError as e:
        print(f"❌ Permission Error: {e.message}")
    except RoseAPIError as e:
        print(f"❌ API Error: {e.message} (status={e.status_code or 'unknown'})")
    return None


def test_token(token_info: dict) -> bool:
    """Test the created token by making a simple API call."""
    if not token_info or not token_info.get("access_token"):
        print("⚠️  No token to test")
        return False

    print("\n🧪 Testing the token...")
    test_client = RoseClient(base_url=BASE_URL, access_token=token_info["access_token"])

    try:
        health = test_client.health_check()
        print(f"✅ Token works! Health check: {health}")
        roles = test_client.roles.list()
        print(f"✅ Found {len(roles)} roles in the account")
        return True
    except RoseAPIError as e:
        print(f"❌ Token test failed: {e.message}")
        return False


def main():
    print("Rose API - Simple Account Creation Demo")
    print("=" * 50)

    result = create_account_with_token()

    if not result:
        print("\n❌ Failed to create account and token")
        return

    print(f"\n🎉 Success!")
    print(f"   Account: {result['account_id']}")
    print(f"   Token: {result['access_token'][:20]}...")

    if test_token(result):
        print("\n✅ Everything works perfectly!")
    else:
        print("\n⚠️  Account created but token has limited permissions")


if __name__ == "__main__":
    main()
