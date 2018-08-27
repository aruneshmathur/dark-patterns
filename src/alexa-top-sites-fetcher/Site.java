public class Site {

	private String url;
	private int globalRank;
	private int countryRank;
	private double reachPerMillion;
	private double pageViewsPerMillion;
	private double pageViewsPerUser;

	public Site() {

	}

	public String getUrl() {
		return url;
	}

	public int getGlobalRank() {
		return globalRank;
	}

	public int getCountryRank() {
		return countryRank;
	}

	public double getReachPerMillion() {
		return reachPerMillion;
	}

	public double getPageViewsPerMillion() {
		return pageViewsPerMillion;
	}

	public double getPageViewsPerUser() {
		return pageViewsPerUser;
	}

	public void setURL(String url) {
		this.url = url;
	}

	public void setGlobalRank(int globalRank) {
		this.globalRank = globalRank;
	}

	public void setCountryRank(int countryRank) {
		this.countryRank = countryRank;
	}

	public void setReachPerMillion(double reachPerMillion) {
		this.reachPerMillion = reachPerMillion;
	}

	public void setPageViewsPerMillion(double pageViewsPerMillion) {
		this.pageViewsPerMillion = pageViewsPerMillion;
	}

	public void setPageViewsPerUser(double pageViewsPerUser) {
		this.pageViewsPerUser = pageViewsPerUser;
	}

	public String toString() {
		return url + ',' + globalRank + ',' + countryRank + ',' + reachPerMillion + ',' + pageViewsPerMillion + ','
				+ pageViewsPerUser;
	}
}
