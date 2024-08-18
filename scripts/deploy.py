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
    mrgl = None
    if click.confirm("Deploy Marginal DAO token?"):
        click.echo("Deploying Marginal DAO token ...")
        mrgl = project.MarginalToken.deploy(
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

    # deploy multi rewards
    if click.confirm("Deploy multi rewards factory?"):
        seconds_until_genesis = click.prompt("Seconds until genesis", type=int)
        genesis = chain.blocks.head.timestamp + seconds_until_genesis
        click.echo(f"Genesis timestamp: {genesis}")

        click.echo("Deploying multi rewards factory ...")
        multirewards_factory = project.MultiRewardsFactory.deploy(
            genesis, sender=deployer, publish=publish
        )
        click.echo(f"Deployed multi rewards factory to {multirewards_factory.address}")

    # deploy points staking
    if click.confirm("Deploy points staking?"):
        mrgl_address = mrgl.address if mrgl is not None else None
        if mrgl_address is None:
            mrgl_address = click.prompt("Marginal DAO token address", type=str)

        click.echo("Deploying points staking ...")
        points = project.StakingPoints.deploy(
            mrgl_address, sender=deployer, publish=publish
        )
        click.echo(f"Deployed points staking to {points.address}")
