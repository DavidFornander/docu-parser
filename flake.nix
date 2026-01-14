{
  description = "Zero-Loss Learning Engine Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config = {
          allowUnfree = true;
          cudaSupport = true;
        };
      };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        name = "docu-parser-env";

        buildInputs = with pkgs; [
          python311
          python311Packages.pip
          python311Packages.virtualenv
          stdenv.cc.cc.lib
          zlib
          glib
          libGL
          libglvnd
          glibc.bin 
          cudaPackages.cuda_nvcc
        ];

        # The Magic: NIX_LD setup to allow pip wheels to run
        NIX_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
          pkgs.stdenv.cc.cc
          pkgs.zlib
          pkgs.glib
          pkgs.libGL
          pkgs.libglvnd
          pkgs.glibc
        ];
        
        NIX_LD = pkgs.lib.fileContents "${pkgs.stdenv.cc}/nix-support/dynamic-linker";

        shellHook = ''
          echo "🚀 Welcome to the Zero-Loss Engine Dev Shell!"
          echo "🔧 Setting up Python environment..."
          
          # Create venv if not exists
          if [ ! -d ".venv" ]; then
            python -m venv .venv
            echo "Created .venv"
          fi
          
          source .venv/bin/activate
          
          # Fix for library loading
          export LD_LIBRARY_PATH=$NIX_LD_LIBRARY_PATH:/run/opengl-driver/lib:$LD_LIBRARY_PATH
          
          echo "✅ Ready! Run 'pip install -r requirements.txt' to install deps."
        '';
      };
    };
}
