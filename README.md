# kiwi-scp

[![Build Status](https://github.drone.yavook.de/api/badges/ldericher/kiwi-scp/status.svg)](https://github.drone.yavook.de/ldericher/kiwi-scp)

> `kiwi` - simple, consistent, powerful

The simple tool for managing container servers


## Quick start

- Learn to use `docker` with `docker-compose`
- Install `kiwi-scp`
- Look at [the example instance](./example)
- Look at the output of `kiwi --help`
- Start building your own instances


## Installation

A convenience installer is available as [install.sh](./dist/install.sh) in the `dist` directory.
You can `curl | sh` it using the following one-liner.

```shell script
curl --proto '=https' --tlsv1.2 -sSf 'https://raw.githubusercontent.com/ldericher/kiwi-scp/master/dist/install.sh' | sh
```

The installer downloads the `kiwi` launcher script and installs it to a location of your choice.
Please consider installing into a directory inside your `$PATH`.
Run in a root shell or use `sudo sh` at the end instead for system-wide installation.

You should then be able to run `kiwi list --show` and see the default configuration file.
This installs the latest version of the kiwi-scp package and sets it up for you.


### Adjusting environment for `kiwi`

The `kiwi` executable depends on [Python](https://www.python.org/) 3.6.1 (or later) and 
[less](http://www.greenwoodsoftware.com/less/) being in your `$PATH`.

In some cases, notably when using a multi-version system such as
[CentOS SCL](https://wiki.centos.org/AdditionalResources/Repositories/SCL), not all of these are in your `$PATH`
at login time.

In those cases, you can simply create a `.kiwi_profile` file in your home directory.
It will be sourced every time you use the `kiwi` command.
For the aforementioned case where you installed `centos-release-scl` and `rh-python36`, your `~/.kiwi_profile` should contain:

```shell script
#!/bin/sh

. /opt/rh/rh-python36/enable
```


## Get started

### Create a kiwi-scp instance

Any directory is implicitly a valid kiwi-scp instance using the default configuration.
To prevent surprises however, you should run `kiwi init` and follow its directions to create a `kiwi.yml` for your instance before using `kiwi` more.


### Concept

A kiwi-scp instance is a directory containing a bunch of static configuration files.
"Static" there as in "those don't change during normal service operation".
These files  could be anything from actual `.conf` files to entire html-web-roots.

Non-static, persistent files are to be kept in a "service data storage", by default the directory `/var/local/kiwi`.
In your `docker-compose.yml` files, you can refer to that directory as **${KIWI_INSTANCE}**.

Start the current kiwi-scp instance using `kiwi up`, or stop it using `kiwi down`.
This also manages kiwi's internal hub network, which you can use as **kiwi_hub** in your `docker-compose.yml` files.


### Projects

A kiwi-scp instance usually contains several projects.
A project is a collection of dependent or at least logically connected services, described by a `docker-compose.yml`.
A well-known example would be webserver + php + database.

To create a project, use the `kiwi new <project-name>` command.
By default, this creates a new disabled project.
Before enabling or starting, consider editing the new project's `docker-compose.yml` file to your liking.
Finally, enable it with `kiwi enable <project-name>`.
You can also create, enable or (analogously) disable multiple projects in a single command.

Each project will have its own place in the service data directory, which you can refer to as **${KIWI_PROJECT}**.

Finally, start a project using `kiwi up <project-name>`.


### Advanced kiwi usage

kiwi-scp extends the logical bounds of `docker-compose` to handling multiple projects.


#### The `kiwi_hub`

With kiwi-scp, you get the internal `kiwi_hub` network for free.
It allows for network communication between services in different projects.
Be aware, services only connected to the kiwi_hub can't use a port mapping!
In most cases, you will want to use this:

```yaml
networks:
  - default
  - kiwi_hub
```


#### The `KIWI_CONFIG` 

Sometimes, it's convenient to re-use configuration files across projects.
For this use case, create a directory named `config` in your instance.
In your `docker-compose.yml` files, you can refer to that directory as **${KIWI_CONFIG}**.


#### `kiwi.yml` options

##### `version`
Version of kiwi-scp to use for this instance.

Default: Version of [`master` branch](https://github.com/ldericher/kiwi-scp/tree/master).

##### `shells`
Sequence of additionally preferable shell executables when entering service containers.

Default: `- /bin/bash`  
Example:

```yaml
runtime:
  shells:
    - /bin/zsh
    - /bin/fish
```

##### `projects`
Sequence of project definitions in this instance.

###### Project definition
Defining a project in this instance. Any subdirectory with a `docker-compose.yml` should be considered a project. The directory name is equivalent to the project name.

Format[^1]: Mapping using the keys `name` (required), `enabled` and `override_storage`
Example:

```yaml
- name: "hello_world"
  enabled: true
```

##### `environment`
Custom variables available in projects' `docker-compose.yml` files.

Format[^1]: Mapping of `KEY: "value"` pairs  
Example:

```yaml
environment:
  HELLO: "World"
  FOO: "Bar"
```

##### `storage`
Configuration for the service data storage.

Format: Mapping using the key `directory`  
Example:

```yaml
storage:
  directory: "/var/local/kiwi"
```

###### `storage:directory`
Path to the local service data directory, the only currently supported service data storage. 
Available as **${KIWI_INSTANCE}** in projects.

Default: `"/var/local/kiwi"`


##### `network`
Configuration for the internal `kiwi_hub` network.

Format: Mapping using the keys `name` and `cidr`
Example:

```yaml
network:
  name: "kiwi_hub"
  cidr: "10.22.46.0/24"
```

###### `network:name`
Configuration for the internal `kiwi_hub` network.

Default: `"kiwi_hub"`

###### `network:cidr`
[CIDR notation](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing#IPv4_CIDR_blocks) for the subnet of the internal `kiwi_hub` network.

Default: `"10.22.46.0/24"`

<font size="5">**For everything else, look at `kiwi --help`**

**Happy kiwi-ing!**</font>

[^1]: This is the officially correct format. For enabling varying conventions, there are multiple accepted formats. Start trying and check with `kiwi list --show` -- if it makes sense, it will likely just work.
