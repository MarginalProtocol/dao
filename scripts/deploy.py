import click

from ape import accounts, chain, project


def main():
    click.echo(f"Running deploy.py on chainid {chain.chain_id} ...")

    deployer_name = click.prompt("Deployer account name", default="")
    deployer = (
        accounts.load(deployer_name)
        if deployer_name != ""
        else accounts.test_accounts[0]
    )
    click.echo(f"Deployer address: {deployer.address}")
    click.echo(f"Deployer balance: {deployer.balance / 1e18} ETH")

    admin_addr = click.prompt("Marginal DAO admin address", type=str)
    publish = click.prompt("Publish to Etherscan?", default=False)

    # deploy marginal dao token
    if click.confirm("Deploy Marginal DAO token?"):
        click.echo("Deploying Marginal DAO token ...")
        mrgl = project.Mrgl.deploy(
            sender=deployer,
            publish=publish,
        )
        click.echo(f"Deployed Marginal DAO token to {mrgl.address}")

        # set owner to admin address and transfer initial mint to admin
        if admin_addr != deployer.address:
            click.echo("Transferring initial supply to Marginal DAO admin ...")
            initial_supply = mrgl.initialSupply()
            symbol = mrgl.symbol()
            decimals = mrgl.decimals()
            mrgl.transfer(admin_addr, initial_supply, sender=deployer)
            click.echo(
                f"Transferred initial supply of {initial_supply / 10**decimals} {symbol} to {admin_addr}"
            )

            click.echo("Setting Marginal DAO token owner to admin ...")
            mrgl.setOwner(admin_addr, sender=deployer)
            click.echo(f"Set Marginal DAO token owner to {admin_addr}")
